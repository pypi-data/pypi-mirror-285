#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gc
import sys
import json
import argparse
import traceback
try:
    sys.path.append("/mnt/e/jiutian/pyproj/PipeGraphPy/src")
except:
    pass

from PipeGraphPy.db import models as db

from PipeGraphPy import graph_run
from PipeGraphPy import graph_predict
from PipeGraphPy import graph_evaluate
from PipeGraphPy import graph_backtest
from PipeGraphPy.constants import STATUS
from dbpoolpy import close_pool

jobtype_info = {
        "run": {"params_field": "run_params", "func": graph_run},
        "schedule": {"params_field": "run_params", "func": graph_run},
        "predict": {"params_field": "predict_params", "func": graph_predict},
        "evaluate": {"params_field": "evaluate_params", "func": graph_evaluate},
        "backtest": {"params_field": "backtest_params", "func": graph_backtest},
    }

def run(jobtype, graph_ids, params=None):
    res = 0
    try:
        graph_ids = map(int, str(graph_ids).split(","))
        # 取执行参数
        kw = None
        try:
            kw = json.loads(params) if params else {}
        except:
            raise Exception("params传值不是json格式")
        for graph_id in graph_ids:
            try:
                run_params_json = db.GraphsTB.map_one(jobtype_info[jobtype]["params_field"]).where(id=graph_id)
                run_params = json.loads(run_params_json) if run_params_json else {}
                if kw:
                    run_params.update(kw)
                func = jobtype_info[jobtype]["func"]
                func(graph_id, **run_params)
            except:
                print(traceback.format_exc())
            finally:
                gc.collect()
    except:
        print(traceback.format_exc())
    finally:
        close_pool()
    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-jobtype", required=True, help="job类型")
    parser.add_argument("-graph_ids", required=True, help="模型id")
    parser.add_argument("-params", required=False,  help="额外参数, json格式的字符串")
    args = parser.parse_args()
    run(args.jobtype, args.graph_ids, args.params)
