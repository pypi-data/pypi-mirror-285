import os
import sys
import time
import argparse
import socket
import traceback
try:
    sys.path.append("/mnt/e/jiutian/pyproj/PipeGraphPy/src")
except:
    pass
from datetime import datetime, timedelta
from PipeGraphPy.db import models as db
from PipeGraphPy.utils import osutil
from PipeGraphPy.shell_op import get_running_graphs, get_ps_list
from PipeGraphPy.constants import STATUS

HEARTBEAT_INTERVAL = int(os.environ.get("MLF_HEARTBEAT_INTERVAL") or 8)
OFFLINE_TIMEOUT = int(os.environ.get("MLF_OFFLINE_TIMEOUT") or 60)


def get_host_info():
    # mbps = osutil.get_disk_mbps()
    cpu = osutil.get_cpu_usage()
    memory = osutil.get_memory_usage()
    disk = osutil.get_disk_usage()
    load = osutil.get_load()
    # return f"mbps:{mbps}MB/s, cpu:{cpu}%, memory:{memory}%, disk:{disk}%, load:{load}"
    return f"cpu:{cpu}%, memory:{memory}%, disk:{disk}%, load:{load}"


def run(name, jobtype):
    """
    执行器心跳监控
    """
    hostname = ''
    for i in range(10):
        try:
            # 执行器名称是否已经存在
            worker_info = db.WorkerTB.find_one(name=name)
            if worker_info:
                if worker_info["is_running"]:
                    raise Exception("已经存在相同名称的执行器:%s 正在运行" % name)
                else:
                    db.WorkerTB.rm(id=worker_info["id"])

            now = datetime.utcnow() + timedelta(hours=8)
            # 获取主机名和IP地址
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            db.WorkerTB.add(
                name=name,
                host_name=hostname,
                jobtype=jobtype,
                utime=now,
                is_running=1,
                host_ip=ip_address,
                host_info=get_host_info()
            )
            break
        except:
            print(traceback.format_exc())
            time.sleep(OFFLINE_TIMEOUT)


    while True:
        try:
            now = datetime.utcnow() + timedelta(hours=8)

            # 取正在运行的模型个数
            os_running_graphs = get_running_graphs()
            os_pid_dict = {(i["graph_ids"],i["pid"]):i for i in os_running_graphs}
            db_running_graphs = db.RunnningGraphTasksTB.find(worker_name=name, jobtype=jobtype)
            db_pid_dict = {(i["graph_ids"],i["pid"]):i for i in db_running_graphs}
            db_diff_os = set(list(db_pid_dict.keys())) - set(list(os_pid_dict.keys()))
            os_diff_db =  set(list(os_pid_dict.keys())) - set(list(db_pid_dict.keys()))
            os_same_db = set(list(os_pid_dict.keys()))&set(list(db_pid_dict.keys()))

            # 数据库多余的任务处理
            if db_diff_os:
                db.RunnningGraphTasksTB.rm(pid=("in", [i[1] for i in db_diff_os]))
                graph_ids = []
                for i in db_diff_os:
                    graph_ids.extend(list(map(int, str(i[0]).split(","))))
                if graph_ids:
                    if jobtype == "run":
                        db.GraphsTB.set(status=STATUS.ERROR).where(status=STATUS.RUNNING, id=("in", graph_ids))
                    elif jobtype == "schedule":
                        db.GraphsTB.set(status=STATUS.ERROR).where(status=STATUS.RUNNING, id=("in", graph_ids))
                    elif jobtype == "predict":
                        db.GraphsTB.set(p_status=STATUS.ERROR).where(p_status=STATUS.RUNNING, id=("in", graph_ids))
                    elif jobtype == "evaluate":
                        db.GraphsTB.set(e_status=STATUS.ERROR).where(e_status=STATUS.RUNNING, id=("in", graph_ids))
                    elif jobtype == "backtest":
                        db.GraphsTB.set(b_status=STATUS.ERROR).where(b_status=STATUS.RUNNING, id=("in", graph_ids))
                    else:
                        pass

            # 系统多的任务处理
            if os_diff_db:
                new_tasks = []
                for i in os_diff_db:
                    new_tasks.append({
                        "host_name": hostname,
                        "jobtype":jobtype,
                        "utime": now,
                        "worker_name": name,
                        "pid": i[1],
                        "graph_ids": i[0]
                    })
                if new_tasks:
                    db.RunnningGraphTasksTB.add_batch(new_tasks)

            # 已经正在运行的任务处理
            if os_same_db:
                values = []
                where = []
                for i in os_same_db:
                    values.append({
                        "utime":now,
                        "duration": (now-db_pid_dict[i]["ctime"]).total_seconds(),
                    })
                    where.append({"pid": i[1]})
                if values and where:
                    db.RunnningGraphTasksTB.set_batch(many_values=values, many_where=where)


            # 查看执行器是否在线
            worker_process = get_ps_list(["worker_subscriber", name, jobtype])
            is_running = 0 if len(worker_process) <= 1 else 1
            print(worker_process)

            # 更新执行器时间
            db.WorkerTB.set(
                utime=now,
                host_info=get_host_info(),
                running_task_num=len(os_running_graphs),
                is_running=is_running
            ).where(name=name,jobtype=jobtype)
        except:
            print(traceback.format_exc())

        time.sleep(HEARTBEAT_INTERVAL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-name", required=True, help="执行器名称")
    parser.add_argument("-jobtype", required=True, help="执行器类型:run, schedule, predict, evaluate, backtest")
    args = parser.parse_args()
    run(args.name, args.jobtype)
