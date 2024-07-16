import json
import traceback
from datetime import datetime, timedelta
from PipeGraphPy.db.models import GraphsTB, NodesTB, ObjectsTB
from dbpoolpy import connect_db
from PipeGraphPy.logger import rlog
from PipeGraphPy.constants import BIZ_TYPE, STATUS, DB


def update_node_params(node_ids, key, value, value_key="value"):
    """更新节点的params字段信息
    parametes:
        node_ids: list or int 要更新节点的id
        key: str 要更新的键
        value: str 要更新的值
    """
    if isinstance(node_ids, int):
        node_ids = [node_ids]
    elif isinstance(node_ids, list):
        node_ids = node_ids
    else:
        raise Exception("update_node_params函数node_ids字段传值类型不合法")
    for node_id in node_ids:
        node_info = NodesTB.find_one(id=node_id)
        node_params = json.loads(node_info["params"])
        for i in node_params:
            if i["key"] == key:
                i[value_key] = value
                break
        NodesTB.set(params=json.dumps(node_params)).where(id=node_id)


def insert_batch(dbserver, table, datas, num=2000):
    try:
        cnt = 0
        with connect_db(dbserver) as db:
            while len(datas) > cnt:
                ceil_list = datas[cnt : cnt + num]
                db.insert(table).many(ceil_list).execute()
                cnt += num
    except Exception:
        rlog.error(traceback.format_exc())


def df_to_db(dbserver, table, df):
    if df.empty:
        return
    datas = df.to_dict(orient="records")
    insert_batch(dbserver, table, datas)


def get_npmos_info(prod_id, instance_id):
    """获取npmos的信息
    params:
        prod_id: 产品id,
        instance_id: 产品实例id
    """
    try:
        biz_info = {}
        with connect_db(DB.dbPipeGraphPy) as npmos_db:
            def get_entity_info(service_entity_rel_type):
                """
                service_entity_rel_type
                1:farm_info, 2:fans_info, 3:wind_tower_info 4:point_info, 5:sys_region 6:sys_region 7:sys_region  8:sys_region
                """
                farm_ids = [i.get("type_id") for i in service_entity_rel_type if i.get("type") == "1"]
                fans_ids = [i.get("type_id") for i in service_entity_rel_type if i.get("type") == "2"]
                wind_tower_ids = [i.get("type_id") for i in service_entity_rel_type if i.get("type") == "3"]
                point_ids = [i.get("type_id") for i in service_entity_rel_type if i.get("type") == "4"]
                region_ids = [i.get("type_id") for i in service_entity_rel_type if i.get("type") in ["5","6","7","8"]]
                # 取实体信息
                farm_info = npmos_db.select("public.farm_info").where(id=("in", farm_ids)).all() if farm_ids else []
                fans_info = npmos_db.select("public.fans_info").where(id=("in", fans_ids)).all() if fans_ids else []
                wind_tower_info = npmos_db.select("public.wind_tower_info").where(id=("in", wind_tower_ids)).all() if wind_tower_ids else []
                point_info = npmos_db.select("public.point_info").where(id=("in", point_ids)).all() if point_ids else []
                sys_region = npmos_db.select("public.sys_region").where(id=("in", region_ids)).all() if region_ids else []
                return {
                    "farm_info":farm_info,
                    "fans_info":fans_info,
                    "wind_tower_info":wind_tower_info,
                    "point_info":point_info,
                    "sys_region":sys_region,
                }
            # 产品信息
            pro_base_info = npmos_db.select("public.pro_base_info").where(id=prod_id).first()
            if not pro_base_info:
                raise Exception("未取到NPMOS产品信息:%s" % prod_id)
            # 产品实例
            pro_instance_info = npmos_db.select("public.pro_instance_info").where(id=instance_id).first()
            if not pro_instance_info:
                raise Exception("未取到NPMOS产品实例信息: %s" % instance_id)
            # 服务实体
            service_entity = npmos_db.select("public.service_entity").where(id=pro_instance_info["srv_entity_id"]).first()
            # 取建模对象
            if service_entity:
                # 实体信息：类型;1-点位-场站;2-点位-风机;3-点位-测风塔;4-点位-自定义点位;5-区域-行政区域;6-区域-地理区域;7-区域-流域;8-区域-自定义区域
                service_entity_rel_type_1 = npmos_db.select("public.service_entity_rel_type").where(srv_data_id=service_entity["id"]).all()
                service_entity["entity_info"] = get_entity_info(service_entity_rel_type_1)
            model_object = {}
            # 从产品实例里找模型对象(旧)
            try:
                # 取建模对象
                pro_instance_srv_rel = npmos_db.select("public.pro_instance_srv_rel").where(pro_instance_id=instance_id).all()
                if pro_instance_srv_rel:
                    service_entity_rel_type_2 = npmos_db.select("public.service_entity_rel_type").where(id=("in", [i["srv_rel_id"] for i in pro_instance_srv_rel])).all()
                    model_object = get_entity_info(service_entity_rel_type_2)
                    farm_info = model_object["farm_info"][0]
            except:
                pass
            # 从服务实体里找模型对象(新)
            if not model_object:
                service_entity_rel_object = npmos_db.select("public.service_entity_rel_object").where(srv_data_id=service_entity["id"]).all()
                if service_entity_rel_object:
                    service_entity_rel_type_2 = npmos_db.select("public.service_entity_rel_type").where(
                            srv_data_id=service_entity["id"],
                            type_id=("in", [i["point_id"] for i in service_entity_rel_object])).all()
                    model_object = get_entity_info(service_entity_rel_type_2)
            biz_info = {
                "product_info": pro_base_info,
                "product_instance_info": pro_instance_info,
                "service_entity": service_entity,
                "model_object": model_object
            }
            return biz_info
    except:
        err = traceback.format_exc()
        return {"msg": "error", "content": err}


def get_biz_info(biz_type_code, biz_id):
    """获取业务信息
    参数：
        biz_type_code: 业务类型
        biz_id：业务id
    """
    if biz_type_code == BIZ_TYPE.WFID:
        return {"biz_type_code": biz_type_code, "biz_id": biz_id}
    elif biz_type_code == BIZ_TYPE.CUSTOM:
        return {"biz_type_code": biz_type_code, "biz_id": biz_id}
    else:
        npmos_info = get_npmos_info(biz_type_code, biz_id)
        if npmos_info.get("msg") == "error":
            biz_info = ObjectsTB.find_one(biz_type_code=biz_type_code, biz_id=biz_id)
            biz_info = biz_info if biz_info else {"biz_type_code": biz_type_code, "biz_id": biz_id}
            biz_info["npmos_info"] = npmos_info
            return biz_info
        else:
            return npmos_info

def graphs_wait_to_run(graph_ids):
    """模型进入训练队列"""
    if graph_ids:
        running_ids = GraphsTB.map("id").where(
                status=("in", [STATUS.RUNNING, STATUS.WAITRUN]),
                id=("in",graph_ids))
        if running_ids:
            graph_ids = list(set(graph_ids) - set(running_ids))
        if graph_ids:
            now = (datetime.utcnow()+timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            GraphsTB.set(
                status=STATUS.WAITRUN,
                wait_run_time=now,
                task_id=''
            ).where(id=("in", graph_ids))

def graphs_wait_to_predict(graph_ids, clock="12", is_pub=False, **kwargs):
    """模型进入预测队列"""
    params = {"clock": clock, "is_pub": is_pub}
    if kwargs:
        params.update(kwargs)
    if graph_ids:
        predicting_ids = GraphsTB.map("id").where(
                p_status=("in", [STATUS.RUNNING, STATUS.WAITRUN]),
                id=("in",graph_ids))
        if predicting_ids:
            graph_ids = list(set(graph_ids) - set(predicting_ids))
        if graph_ids:
            now = (datetime.utcnow()+timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            GraphsTB.set(
                p_status=STATUS.WAITRUN,
                predict_params=json.dumps(params),
                wait_predict_time=now,
            ).where(id=("in", graph_ids))
