# -*- coding: utf-8 -*-

import logging
import datetime
from tornado import gen
from . import user_mongo_defines as user_def
# from .sys_config import SysConfig
from configs import type_defines
import pymongo
from ..mongo_dao_base import MongoDAOBase

logger = logging.getLogger(__name__)


class UserMongoDAOException(Exception):
    def __init__(self, message, *args):
        self._msg = message % tuple(args)
    
    def __str__(self):
        return self._msg


class UserMongoDAO(MongoDAOBase):
    def __init__(self, *args, **kwargs):
        MongoDAOBase.__init__(self, *args, **kwargs)
    
    @gen.coroutine
    def add_user_info(self, **kwargs):
        user_info = kwargs 
        
        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.USER_INFOS_TB]
            row = user_def.new_user_infos_row()
            for (k, v) in list(user_info.items()):
                if k in row:
                    row[k] = v
                else:
                    raise UserMongoDAOException("Unknwon user infos row column \"%s\"", k)
            validate_ret, exp_col = user_def.validate_user_infos_row(row)
            if not validate_ret:
                raise UserMongoDAOException("Validate user infos row failed, invalid column \"%s\"", exp_col)
            tb.insert_one(row)
        
        yield self.submit(_callback)
    
    @gen.coroutine
    def update_user_info(self, uid, **kwargs):
        info = kwargs
        #validate_ret, exp_col = user_def.validate_user_infos_cols(**kwargs)
        #if not validate_ret:
            #raise UserMongoDAOException("Validate user infos columns error, invalid column \"%s\"", exp_col)

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.USER_INFOS_TB]
            if "uid" in info:
                del info["uid"]
            res = tb.update_one({"uid": uid}, {"$set": info})
            return res.modified_count
        
        ret = yield self.submit(_callback)
        raise gen.Return(ret) 
    
    @gen.coroutine
    def is_user_info_exists(self, uid):

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.USER_INFOS_TB]
            return tb.count({"uid": uid}) > 0
        
        ret = yield self.submit(_callback)
        raise gen.Return(ret)
    
    @gen.coroutine
    def is_user_info_exists_by_phone_num(self, phone_num):

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.USER_INFOS_TB]
            return tb.count({"phone_num": phone_num}) > 0
        
        ret = yield self.submit(_callback)
        raise gen.Return(ret)
    
    @gen.coroutine
    def get_user_info(self, uid, cols):

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.USER_INFOS_TB]
            qcols = {"_id": 0}
            for v in cols: 
                #if not user_def.has_user_infos_col(v):
                    #raise UserMongoDAOException("Unknown user infos row column \"%s\"", v)
                qcols[v] = 1
            cursor = tb.find({"uid": uid}, qcols)
            if cursor.count() <= 0:
                return None 
            dc = cursor[0]
            # if "logo_url" in dc and dc["logo_url"]:
            #     dc["logo_url"] = SysConfig.current().gen_file_url(type_defines.USER_LOGO_FILE, dc["logo_url"])
            return dc
        
        ret = yield self.submit(_callback)
        raise gen.Return(ret)

    @gen.coroutine
    def get_user_info_by_condictions(self, cols, **kwargs):
        cond = kwargs
        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.USER_INFOS_TB]
            qcols = {"_id": 0}
            for v in cols:
                qcols[v] = 1
            cursor = tb.find(cond, qcols)
            if cursor.count() <= 0:
                return None
            return cursor

        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def add_feedback(self, uid, mobile, message, contact):

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.USER_FEEDBACK_TB]
            row = {}
            row['uid'] = uid
            row['mobile'] = mobile 
            row['message'] = message 
            row['contact'] =contact 
            row['time'] = datetime.datetime.now()
            tb.insert_one(row)

        yield self.submit(_callback)

    @gen.coroutine
    def get_feedback(self):

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.USER_FEEDBACK_TB]
            cursor = tb.find({}, sort=[("time", pymongo.DESCENDING)]).limit(100)
            return cursor

        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def get_uid_by_mobile(self, phone_num):
        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.USER_INFOS_TB]
            cursor = tb.find({"phone_num": phone_num}, {"_id": 0, "uid": 1})
            if cursor.count() <= 0:
                return None
            else:
                return cursor[0]["uid"]
        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def update_trace_log(self, msg_id, router, **kwargs):

        """
        更新追踪日志
        :param msg_id:  ID
        :param router:  路由信息
        :param kwargs:
        uid:
        用户UID

        traceId:
        各推送返回的唯一追踪ID

        result:
        -1:发送失败   0: 发送成功

        device_type:
        1:android       2:ios

        recv_result:
        接收结果:
        -1:未知   0:成功送达   1：用户没有登陆    2：用户没有打开APP

        confirm_time:
        确认送达结果的时间

        :return:
        """
        info = kwargs
        # logging.debug("update_trace_msg:%s", info)

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.MSG_SENDING_TB]
            info["msg_id"] = msg_id
            info["router"] = router
            info['updateTime'] = datetime.datetime.now()
            tb.update_one({"msg_id": msg_id, "router": router}, {"$set": info}, upsert=True)
        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def add_msg_log(self, **kwargs):
        info = kwargs

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.MSG_TB]
            tb.insert(info)

        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def update_msg_log(self, msg_id, **kwargs):
        info = kwargs

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.MSG_TB]
            res = tb.update_one({"msg_id": msg_id}, {"$set": info})
            # logging.debug("update_msg_msg,msg_id:%s info:%s, res.modified_count:%d", msg_id, info, res.modified_count)

        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def delete_sending_msg(self, msg_id, router):

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.MSG_SENDING_TB]
            tb.delete_one({"msg_id": msg_id, "router": router})

        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def get_hist_msg_log(self, start_date, end_date, uid):

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.MSG_TB]
            find_cond = {"uid": uid, "updateTime": {"$gte": start_date}}
            if end_date:
                find_cond["updateTime"]["$lte"] = end_date
            cursor = tb.find(find_cond).sort("updateTime", pymongo.DESCENDING)
            return cursor

        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def get_hist_msg_by_msgid(self, uid, begin_msgid=-1, limit=10):

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.MSG_TB]
            if begin_msgid < 0:
                find_cond = {"uid": uid}
            else:
                find_cond = {"uid": uid, "msg_id": {"$lt": begin_msgid}}
            cursor = tb.find(find_cond).sort("msg_id", pymongo.DESCENDING).limit(limit)
            return cursor

        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def get_max_msg_id(self, uid):

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.MSG_TB]
            find_cond = {"uid": uid}
            cursor = tb.find(find_cond).sort("msg_id", pymongo.DESCENDING).limit(1)
            if cursor.count() > 0:
                return cursor[0]['msg_id']
            else:
                return -1

        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def get_sending_task(self, msg_id, router):

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.MSG_SENDING_TB]
            cols={
                "router": 1,
                "msg_id": 1,
                "push_type": 1,
                "trace_id": 1,
                "msg_type": 1,
                "uid": 1,
                "device_type": 1,
                "result": 1,
                "retry": 1,
                "send_time": 1,
                "payload": 1,
                "desc": 1,
                "content": 1,
            }
            res = tb.find({"msg_id": msg_id, "router": router}, cols)
            if res.count() > 0:
                return res[0]
            return None
        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def get_msg_id_by_trace_id(self, trace_id):

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.MSG_SENDING_TB]
            res = tb.find({"trace_id": trace_id},{"msg_id": 1})
            if res.count() <=0:
                return None
            return res[0]["msg_id"]

        ret = yield self.submit(_callback)
        return ret


    @gen.coroutine
    def get_all_sending_msg(self, num, minutes=2):

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.MSG_SENDING_TB]
            res = tb.find({"updateTime": {"$lt": datetime.datetime.now() - datetime.timedelta(minutes=minutes)}}).sort(
                "updateTime", pymongo.ASCENDING).limit(num)
            return res

        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def update_sending_msg_result(self, msg_id, result):

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.MSG_SENDING_TB]
            tb.update_one({"msg_id": msg_id, "updateTime": datetime.datetime.now(), "result": result})

        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def retry_send_msg(self, msg_id):

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.MSG_SENDING_TB]
            res = tb.find_and_modify(
                query={"msg_id": msg_id},
                update={"$inc": {"retry": -1}, "$set": {"updateTime": datetime.datetime.now()}})
            if res.count() > 0:
                return res['retry']
            return 0

        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def gen_msg_sn(self):
        """
        生成发送信息唯一序列号
        :return:
        """

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.SN_TB]
            sn_name = user_def.MSG_SN_NAME
            res = tb.find_and_modify(query={"sn_name": sn_name}, update={"$inc": {"seq": 1}}, upsert=True)
            if res:
                seq = res["seq"]
                return seq
            return 0

        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def update_weixin_token(self, token):
        """
        刷新微信公众号token
        :param token:
        :return:
        """

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.SN_TB]
            tb.update_one({"sn_name": "weixin_token"}, {"$set": {"token": token}}, upsert=True)
        ret = yield self.submit(_callback)

        return ret

    @gen.coroutine
    def get_weixin_token(self):
        """
        :return:
        """
        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.SN_TB]
            cur = tb.find({"sn_name": "weixin_token"})
            if cur.count() > 0:
                return cur[0]["token"]
            else:
                return None

        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def __pop(self, queue_name):

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.QUEUE_TB]
            res = tb.find_and_modify(query={"query_name": queue_name}, update={"$pop": {'msg': -1}})
            return res

        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def __push(self, queue_name, msg):

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[user_def.USER_DATABASE][user_def.QUEUE_TB]
            res = tb.find_and_modify(query={'query_name': queue_name}, update={"$push": {'msg': msg}}, upsert=True )
            return res

        ret = yield self.submit(_callback)
        return ret

    @gen.coroutine
    def push_msg(self, template_id, notice, detail, router=None):
        """
        推送一条信息。信息保存在queue，等msg_srv_d轮询读取。发送手段(app/微信/sms）根据msg_srv_d逻辑而定，不在这里指定
        用于通知类消息发送。
        APP推送类发送(例如位置更新/电量状态更新)仍然用原RPC接口直接推送

        :param template_id:  消息类型 ,具体见type_defines.MSG_TYPE
        :param notice: 是否通知状态栏，true :是 false:否
        :param router: 是否指定路由，如果指定路由，则不再根据IMEI寻找所有用户自动发送.默认不指定
        :param detail: 发送内容,字典格式
        :return:
        """
        msg = {
            "template_id": template_id,
            "notice": notice,
            "router": router,
            "detail": detail,
            "time": datetime.datetime.now()
        }
        yield self.__push("msg_queue", msg)

    @gen.coroutine
    def pop_msg(self):
        """
        从queue弹出一条消息进行发送处理
        :return:  msg
        {
            type=type,
            content=content,
            time=time
        }
        """
        ret = yield self.__pop("msg_queue")
        return ret
