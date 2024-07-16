import os
import re
import time
import subprocess

def exe_shell(shell_script):
    p = subprocess.Popen(shell_script, shell=True, stdout=subprocess.PIPE)
    out = p.stdout.readlines()
    return [str(i.decode("utf-8")).strip('\n') for i in out]


def run_graph(graph_id):
    return os.system(f"python worker_exe.py -jobtype run -graph_ids {graph_id} > /dev/null &")


def schedule_graph(graph_id):
    return os.system(f"python worker_exe.py -jobtype schedule -graph_ids {graph_id} > /dev/null &")


def predict_graph(graph_id):
    return os.system(f"python worker_exe.py -jobtype predict -graph_ids {graph_id} > /dev/null &")


def evaluate_graph(graph_id):
    return os.system(f"python worker_exe.py -jobtype evaluate -graph_ids {graph_id} > /dev/null &")


def backtest_graph(graph_id):
    return os.system(f"python worker_exe.py -jobtype backtest -graph_ids {graph_id} > /dev/null &")


def get_ps_list(greps=None):
    """任务列表， greps过滤条件，不能加空格"""
    sh_res = ""
    if greps:
        if isinstance(greps, list):
            grep_str = " | ".join([f"grep {i}" for i in greps])
            sh_res = exe_shell(f"ps -ef | {grep_str}")
        elif isinstance(greps, str):
            sh_res = exe_shell(f"ps -ef | grep {greps}")
    else:
        sh_res = exe_shell("ps -ef")
    return sh_res

def get_running_graphs(graph_id=None, jtype=None):
    """取正在运行的模型
    params:
        graph_id: 模型id
        jtype: 任务类型: run, schedule, predict, evaluate, backtest
    解析进程：['zsq', '7545', '4453', '99', '17:22', 'pts/2', '00:00:02', 'python', 'worker_exe.py', '-jobtype', 'run', '-graph_ids', '721']
    """
    greps = ["python", "worker_exe", "jobtype", "graph_ids"]
    if graph_id:
        greps.append(str(graph_id))
    if jtype:
        greps.append(str(jtype))
    job_lst = get_ps_list(greps)
    running = []
    for i in job_lst:
        infos = re.split(r"\s+", i)
        if infos[-2] == "-graph_ids":
            running.append({
                "pid": int(infos[1]),
                "ppid": int(infos[2]),
                "graph_ids": infos[-1],
                "jtype": infos[-3].replace(".py", "")
            })
    return running


def get_all_child_pid(ppid):
    """
    取所有的子进程id
    """
    job_lst = get_ps_list(str(ppid))
    pids = []
    for i in job_lst:
        infos = re.split(r"\s+", i)
        if infos[2] == str(ppid):
            pids.append(infos[1])
    return pids


def pid_is_running(pid):
    """
    判断某个进程是否在运行
    """
    job_lst = get_ps_list(str(pid))
    is_running = False
    for i in job_lst:
        infos = re.split(r"\s+", i)
        if infos[1] == str(pid):
            is_running = True
            break
    return is_running


def kill_pid(pid):
    """
    杀掉进程和子进程
    """
    # 杀掉子进程 pkill -P ppid
    child_pids = get_all_child_pid(pid)
    if child_pids:
        os.system(f"pkill -P {pid}")
    # 杀掉父进程 kill pid
    os.system(f"kill {pid}")
    # 等待1秒
    time.sleep(1)
    if child_pids:
        if any([pid_is_running(i) for i in child_pids]):
            for i in child_pids:
                os.system(f"kill %s" % i)
            time.sleep(1)
    # 查看子进程是否存在
    child_pids = get_all_child_pid(pid)
    if child_pids:
        for i in child_pids:
            os.system(f"kill %s" % i)
        time.sleep(1)
    # 查看父进程是否还存在
    if pid_is_running(pid):
        os.system(f"kill {pid}")
        time.sleep(1)
    # 做最终判断
    if not pid_is_running(pid):
        return True
    else:
        return False


def kill_graph_job(graph_id, jtype="run"):
    """停止正在执行的模型任务
    params:
        graph_id: 模型id
        jtype: 任务类型: run, schedule predict, evaluate, backtest
    """
    # 取出训练进程
    graph_jobs = get_running_graphs(graph_id, jtype)
    if graph_jobs:
        if all([kill_pid(i["pid"]) for i in graph_jobs]):
            return True
        else:
            return False
