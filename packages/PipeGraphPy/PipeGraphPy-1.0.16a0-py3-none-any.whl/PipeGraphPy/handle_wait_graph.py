#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
运行等待运行的模型
"""

import sys
import os
import json
import copy

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import traceback
import pandas as pd
from collections import namedtuple
from datetime import datetime, timedelta
from PipeGraphPy.db import models as db
from PipeGraphPy.config import settings
from PipeGraphPy.constants import STATUS, GRAPHTYPE
from rabbitmqpy import Puber
from croniter import croniter
import logging

global NOW

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)

sleep_time_between_run = 0.5
sleep_time = int(os.environ.get("WAIT_RUN_SLEEP_TIME") or 7)    # 两个模型运行时间间隔
max_run_num = int(os.environ.get("WAIT_RUN_MAX_RUN_NUM") or 15)   # 最大正在运行数量
max_try_time = int(os.environ.get("WAIT_RUN_MAX_TRY_TIME") or 15)  # 一个模型尝试运行次数
offline_interval = int(os.environ.get("WAIT_RUN_OFFLINE_INTERVAL") or 60)  # 一个模型尝试运行次数
send_timeout = int(os.environ.get("SEND_TIMEOUT") or 120)  # 发送后不运行的超时时间（秒）
run_timeout = int(os.environ.get("RUN_TIMEOUT") or (3600*6))  # 发送后不运行的超时时间（秒）
predict_timeout = int(os.environ.get("PREDICT_TIMEOUT") or 1200)  # 发送后不运行的超时时间（秒）

JobInfo = namedtuple("JobInfo", "jobtype, status_field, crontab_text_field, record_id_field, record_table, crontab_able_field, wait_time_field, max_num, timeout, able")
job_infos = [
    JobInfo(jobtype="run",
            status_field="status",
            crontab_text_field="crontab_run_text",
            record_id_field="run_record_id",
            record_table=db.RunRecordTB,
            crontab_able_field="crontab_run_able",
            wait_time_field="wait_run_time",
            max_num=10,
            timeout=run_timeout,
            able=1),
    JobInfo(jobtype="schedule",
            status_field="status",
            crontab_text_field="crontab_run_text",
            record_id_field="run_record_id",
            record_table=db.RunRecordTB,
            crontab_able_field="crontab_run_able",
            wait_time_field="wait_run_time",
            max_num=10,
            timeout=run_timeout,
            able=1),
    JobInfo(jobtype="predict",
            status_field="p_status",
            crontab_text_field="crontab_predict_text",
            record_id_field="predict_record_id",
            record_table=db.PredictRecordTB,
            crontab_able_field="crontab_predict_able",
            wait_time_field="wait_predict_time",
            max_num=60,
            timeout=predict_timeout,
            able=1),
    JobInfo(jobtype="evaluate",
            status_field="e_status",
            crontab_text_field="",
            record_id_field="evaluate_record_id",
            record_table=db.EvaluateRecordTB,
            crontab_able_field="",
            wait_time_field="wait_evaluate_time",
            max_num=10,
            timeout=predict_timeout,
            able=1),
    JobInfo(jobtype="backtest",
            status_field="b_status",
            crontab_text_field="",
            record_id_field="backtest_record_id",
            record_table=db.BacktestRecordTB,
            crontab_able_field="",
            wait_time_field="wait_backtest_time",
            max_num=10,
            timeout=predict_timeout,
            able=1),
]


def get_status_graphs(status_field, jobtype):
    if jobtype == "schedule":
        where = {
                status_field: ("in", [STATUS.RUNNING, STATUS.WAITRUN, STATUS.WAITEXE]),
                "is_del":0,
                "category":GRAPHTYPE.SCHEDULE,
                "available":1
                }
    else:
        where = {
                status_field: ("in", [STATUS.RUNNING, STATUS.WAITRUN, STATUS.WAITEXE]),
                "is_del":0,
                "category":("!=", GRAPHTYPE.SCHEDULE),
                "available":1
                }
    run_graph_infos = db.GraphsTB.find(**where)
    running_graphs = [i for i in run_graph_infos if i[status_field] == STATUS.RUNNING]
    waitrun_send_graphs = [i for i in run_graph_infos if i[status_field] == STATUS.WAITEXE]
    waitrun_unsend_graphs = [i for i in run_graph_infos if i[status_field] == STATUS.WAITRUN]
    return running_graphs, waitrun_send_graphs, waitrun_unsend_graphs


def cal_use_worker(workers, num):
    use_workers = []
    for i in range(num):
        workers = sorted(workers, key=lambda x:x["running_task_num"])
        use_workers.append(workers[0])
        workers[0]["running_task_num"] += 1
    return use_workers


def send_work(worker_name, jobtype, graph_id):
    # 查找可以用来执行任务的执行器,取任务数最少的
    puber = Puber(
        settings.AMQP_URL,
        'pgp_%s_e' % jobtype,
        'direct',
        routing_key='pgp_%s_%s_k' % (worker_name, jobtype),
    )
    now = datetime.utcnow() + timedelta(hours=8)
    puber.send(json.dumps({
        "name": worker_name,
        "jobtype": jobtype,
        "graph_id": graph_id,
        "optype": "exe",
        "send_time": str(now)
    }))

# def wait_send(graph_ids, status_field, wait_time_field):
#     if graph_ids:
#         now = (datetime.utcnow()+timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
#         values = {
#             status_field: STATUS.WAITRUN,
#             wait_time_field: now,
#         }
#         where = {
#             status_field: ("not in", [STATUS.RUNNING, STATUS.WAITRUN]),
#             "id": ("in", graph_ids)
#         }
#         db.GraphsTB.set(**values).where(**where)


def run():
    """运行"""
    num = 1
    send_worker_heartbeat_time = dict()
    trigger_minute = ""
    had_triggered = {}
    graph_waitext_time = {i.jobtype: dict() for i in job_infos}
    while True:
        if num >= max_try_time:
            num = 0
        global NOW
        NOW = datetime.utcnow()+timedelta(hours=8)
        minute = NOW.strftime("%Y%m%d%H%M")
        if minute != trigger_minute:
            had_triggered = {}
            trigger_minute = minute
        for job in job_infos:
            if not job.able:
                continue
            try:
                # 触发定时任务
                # 取所有cron
                if job.crontab_text_field:
                    where = {
                        job.crontab_able_field: 1,
                        job.status_field: ("not in", [STATUS.WAITRUN, STATUS.WAITEXE, STATUS.RUNNING]),
                        "category":GRAPHTYPE.SCHEDULE if job.jobtype=="schedule" else ("!=", GRAPHTYPE.SCHEDULE)
                    }
                    if had_triggered.get((job.jobtype, trigger_minute)):
                        where["id"] = ("not in", had_triggered[(job.jobtype, trigger_minute)])
                    trigger_df = pd.DataFrame(db.GraphsTB.select().fields("id," + job.crontab_text_field).where(**where).all())
                    trigger_df = trigger_df.dropna()
                    if not trigger_df.empty:
                        trigger_df = trigger_df[trigger_df[job.crontab_text_field] != '']
                        trigger_df = trigger_df[trigger_df[job.crontab_text_field].apply(lambda x: croniter.is_valid(x))]
                        trigger_df = trigger_df[trigger_df[job.crontab_text_field].apply(lambda x: croniter.match(x, NOW))]
                        if not trigger_df.empty:
                            trigger_graph_ids = trigger_df["id"].to_list()
                            now = (datetime.utcnow()+timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                            values = { job.status_field: STATUS.WAITRUN, job.wait_time_field: now, }
                            db.GraphsTB.set(**values).where(id=("in",trigger_graph_ids))
                            if (job.jobtype, trigger_minute) in had_triggered:
                                had_triggered[(job.jobtype, trigger_minute)].extend(trigger_graph_ids)
                            else:
                                had_triggered[(job.jobtype, trigger_minute)] = trigger_graph_ids
                        else:
                            logger.info("%s: 没有匹配到触发的模型" % job.jobtype)


                # 查找正在运行和等待运行的模型
                running, send, waitrun = get_status_graphs(job.status_field, job.jobtype)
                logger.info("类型: %s 正在运行个数: %s 等待运行已发送个数: %s 等待运行未发送个数: %s" % (
                    job.jobtype, len(running), len(send), len(waitrun)))

                # 发送超时后重新发送
                if send:
                    # 清理graph_waitext_time变量：
                    drop_graph_ids = set(list(graph_waitext_time[job.jobtype].keys())) - set([i["id"] for i in send])
                    for i in drop_graph_ids:
                        del graph_waitext_time[job.jobtype][i]
                    # 判断超时
                    now = datetime.utcnow()+timedelta(hours=8)
                    for i in send:
                        if i["id"] not in graph_waitext_time[job.jobtype]:
                            graph_waitext_time[job.jobtype][i["id"]] = now
                        else:
                            if (now - graph_waitext_time[job.jobtype][i["id"]]).total_seconds() > send_timeout:
                                logger.info("模型：%s, 发送等待执行:%s 超时" % (i["id"], job.jobtype))
                                values = {job.status_field: STATUS.WAITRUN}
                                db.GraphsTB.set(**values).where(id=i["id"])

                # 清理运行超时模型
                if running:
                    now = datetime.utcnow()+timedelta(hours=8)
                    for i in running:
                        if not i.get(job.record_id_field):
                            logger.info("正在%s的模型:%s 没有运行记录id，将停止运行" % (job.jobtype, i["id"]))
                            values = {job.status_field: STATUS.ERROR}
                            db.GraphsTB.set(**values).where(id=i["id"])
                            continue
                        else:
                            record_info = job.record_table.find_one(id=i[job.record_id_field])
                            if not record_info:
                                logger.info("正在%s的模型:%s 没有运行记录，将停止运行" % (job.jobtype, i["id"]))
                                values = {job.status_field: STATUS.ERROR}
                                db.GraphsTB.set(**values).where(id=i["id"])
                            if record_info["status"] not in [STATUS.RUNNING, STATUS.WAITRUN, STATUS.WAITEXE]:
                                logger.info("正在%s的模型:%s 记录状态不是运行状态，将停止运行" % (job.jobtype, i["id"]))
                                values = {job.status_field: STATUS.ERROR}
                                db.GraphsTB.set(**values).where(id=i["id"])
                            if not record_info.get("ctime"):
                                logger.info("正在%s的模型:%s 记录里没有开始时间，将停止运行" % (job.jobtype, i["id"]))
                                values = {job.status_field: STATUS.ERROR}
                                db.GraphsTB.set(**values).where(id=i["id"])
                                job.record_table.set(status=STATUS.ERROR).where(record_info["id"])
                                job.record_table.add_log(record_info["id"], "ctime字段没有值, 强制停止!!!")
                            if (now - record_info["ctime"]).total_seconds() > job.timeout:
                                logger.info("正在%s的模型:%s 执行超时，将停止运行" % (job.jobtype, i["id"]))
                                values = {job.status_field: STATUS.ERROR}
                                db.GraphsTB.set(**values).where(id=i["id"])
                                job.record_table.set(status=STATUS.ERROR).where(record_info["id"])
                                job.record_table.add_log(record_info["id"], "执行超时，强制停止!!!")

                limit_num = job.max_num - len(running) - len(send)
                if limit_num > 0:
                    if job.jobtype == "schedule":
                        where = {
                                job.status_field: STATUS.WAITRUN,
                                "is_del":0,
                                "category":GRAPHTYPE.SCHEDULE,
                                "available":1
                        }
                    else:
                        where = {
                                job.status_field: STATUS.WAITRUN,
                                "is_del":0,
                                "category":("!=", GRAPHTYPE.SCHEDULE),
                                "available":1
                        }
                    graph_infos = db.GraphsTB.select().where(**where).order_by(job.wait_time_field).limit(limit_num).all()
                    workers = db.WorkerTB.find(jobtype=job.jobtype, is_running=1)
                    if not workers:
                        print("没有正在运行%s的执行器" % job.jobtype)
                        continue
                    use_workers = cal_use_worker(workers, len(graph_infos))
                    for n, info in enumerate(graph_infos):
                        # 查找可以用来执行任务的执行器,取任务数最少的
                        send_work(use_workers[n]["name"], job.jobtype, info["id"])
                    if graph_infos:
                        graph_ids = [i["id"] for i in graph_infos]
                        values = {job.status_field: STATUS.WAITEXE}
                        db.GraphsTB.set(**values).where(id=("in", graph_ids))
                        print("发送%s模型：%s" % (job.jobtype, graph_ids))

                # 更新执行器的状态：
                now = datetime.utcnow() + timedelta(hours=8)
                workers = db.WorkerTB.find(jobtype=job.jobtype, is_running=1)
                for w in workers:
                    if (now-w["utime"]).total_seconds() > offline_interval:
                        db.WorkerTB.set(is_running=0).where(id=w["id"])
                    # 发送worker心跳任务
                    if w.get("worker_heartbeat_able") and w.get("worker_heartbeat_interval") and w.get("worker_heartbeat_graph_id"):
                        if send_worker_heartbeat_time.get(w["name"]):
                            if (now-send_worker_heartbeat_time[w["name"]]).total_seconds() > w["worker_heartbeat_interval"] * 60:
                                send_work(w["name"], job.jobtype, w["worker_heartbeat_graph_id"])
                                send_worker_heartbeat_time[w["name"]] = now
                        else:
                            send_worker_heartbeat_time[w["name"]] = now
                        # 判断心跳执行情况
                        if w["worker_heartbeat_exetime"] and (now-w["worker_heartbeat_exetime"]).total_seconds() > 5 * w["worker_heartbeat_interval"] * 60:
                            if num == 0:
                                print("error!!!, %s调度停止" % w["name"])
            except:
                logger.info(traceback.format_exc())
        time.sleep(sleep_time)
        num += 1

if __name__ == "__main__":
    run()
