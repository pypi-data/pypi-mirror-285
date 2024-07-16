# coding:utf-8

import os
import json
import socket
import traceback
import argparse
from datetime import datetime, timedelta
from rabbitmqpy import Subscriber
from PipeGraphPy.db import models as db
from logging import getLogger
from PipeGraphPy.shell_op import run_graph, schedule_graph, predict_graph, evaluate_graph, backtest_graph, kill_graph_job, get_running_graphs
from PipeGraphPy.config import settings

logger = getLogger()

class WorkerSubscriber(Subscriber):
    """发布订阅者
    订阅mq里的消息，根据发送的执行器名称和jobtype来判断是否要执行
    """

    def __init__(self, name, jobtype):
        self.name = name
        self.jobtype = jobtype
        Subscriber.__init__(
            self,
            settings.AMQP_URL,
            'pgp_%s_e' % self.jobtype,
            'direct',
            'pgp_%s_%s_q' % (self.name, self.jobtype),
            routing_key='pgp_%s_%s_k' % (self.name, self.jobtype),
            auto_ack=False,
        )


    def on_message(self, chan, method_frame, header_frame, body, userdata=None):
        """运行订阅任务
        name: 执行器名称
        jobtype: 标签名
        graph_id: 模型名称
        optype: 操作类型, exe, kill
        """
        try:
            now = datetime.utcnow() + timedelta(hours=8)
            json_data = json.loads(body.decode("utf-8"))
            print(json_data)
            name = json_data.get("name")
            jobtype = json_data.get("jobtype")
            graph_id = int(json_data.get("graph_id"))
            optype = json_data.get("optype")
            send_time = json_data.get("send_time")
            if name != self.name or jobtype != self.jobtype:
                print(f"{self.name} not {self.jobtype}: {name},{jobtype},{graph_id}" )
                return
            else:
                if optype == "exe":
                    if jobtype == "run":
                        run_graph(graph_id)
                    elif jobtype == "schedule":
                        schedule_graph(graph_id)
                    elif jobtype == "predict":
                        predict_graph(graph_id)
                    elif jobtype == "evaluate":
                        evaluate_graph(graph_id)
                    elif jobtype == "backtest":
                        backtest_graph(graph_id)
                    else:
                        raise Exception("jobtype error")
                    print(f"{jobtype}: {graph_id}" )
                    os_running_graphs = get_running_graphs(graph_id=graph_id, jtype=jobtype)
                    for i in os_running_graphs:
                        try:
                            hostname = socket.gethostname()
                            db.RunnningGraphTasksTB.add(
                                host_name=hostname,
                                jobtype=jobtype,
                                utime=now,
                                worker_name=name,
                                pid=i["pid"],
                                graph_ids=i["graph_ids"]
                            )
                            worker = db.WorkerTB.find_one(name=self.name, jobtype=self.jobtype)
                            if worker:
                                db.WorkerTB.set(
                                    running_task_num=worker["running_task_num"]+1
                                ).where(id=worker["id"])
                            else:
                                raise Exception("不存在此执行器")
                        except:
                            print(traceback.format_exc())

                elif optype == "kill":
                    os_running_graphs = get_running_graphs(graph_id=graph_id, jtype=jobtype)
                    kill_res = kill_graph_job(graph_id, jtype=jobtype)
                    if kill_res:
                        for i in os_running_graphs:
                            db.RunnningGraphTasksTB.rm(pid=int(i["pid"]))
                    else:
                        raise Exception(f"删除任务失败：{graph_id}, {jobtype}")

        except Exception:
            logger.error(traceback.format_exc())
        finally:
            chan.basic_ack(delivery_tag=method_frame.delivery_tag)
            print("on message over")


if __name__=='__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-name", required=True, help="执行器名称")
        parser.add_argument("-jobtype", required=True, help="执行器标签:run, schedule, predict, evaluate, backtest")
        args = parser.parse_args()
        subpuber = WorkerSubscriber(args.name, args.jobtype)
        subpuber.start()
    except Exception:
        logger.error(traceback.format_exc())
