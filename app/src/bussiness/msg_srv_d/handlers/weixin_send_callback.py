# -*- coding: utf-8 -*-


import logging
import traceback
from tornado.web import asynchronous
from tornado import gen
from lib import error_codes, type_defines
from lib import xmq_web_handler
import xml.etree.cElementTree as ET
import urllib.parse

logger = logging.getLogger(__name__)


class WeixinSendCallback(xmq_web_handler.XMQWebHandler):

    @asynchronous
    @gen.coroutine
    def _deal_request(self):
        logger.debug("OnWeixinCallback, %s", self.dump_req())
        self.set_header("Content-Type", "application/json; charset=utf-8")
        res = {"status": error_codes.EC_SUCCESS}
        # 获取请求参数
        try:
            data = urllib.parse.unquote(self.get_argument("data"))
            # logger.debug("data:%s", data)
            tree = ET.fromstring(data)
            sending_mgr = self.settings["sending_mgr"]
            user_dao = self.settings["user_dao"]
            xml_dic = {}
            for node in tree:
                xml_dic[node.tag] = node.text
            # logger.debug("xml:%s", xml_dic)
            if xml_dic.get("MsgType", None) != "event":
                return
            if xml_dic.get("Event") == "TEMPLATESENDJOBFINISH":
                # 发送模板消息回调
                if xml_dic.get("Status", None) == "success":
                    trace_id = int(xml_dic["MsgID"])
                    msg_id = yield user_dao.get_msg_id_by_trace_id(trace_id)
                    yield sending_mgr.finish_sending_task(msg_id, type_defines.MSG_TYPE_WEIXIN_PUSH,
                                                          recv_result=type_defines.MSG_RESULT_RECV_SUCCESS)
                    logger.debug("OnWeixinCallback msg_id: %d recv success.", msg_id)
            elif xml_dic.get("Event") == "unsubscribe":
                # 取消关注回调
                wx_openid = xml_dic.get("FromUserName", None)
                user_info = yield user_dao.get_user_info_by_condictions(("uid",), wx_openid=wx_openid)
                if user_info is None:
                    return
                uid = user_info[0].get("uid", 0)
                yield user_dao.update_user_info(uid, wx_openid=None)
                logger.debug("OnWeixinCallback uid: %d unbind weixin push success.", uid)
        except Exception as e:
            logger.warning("OnWeixinCallback, invalid args, %s, %s error:%s", self.dump_req(), traceback.format_exc(),
                           e)
            res["status"] = error_codes.EC_INVALID_ARGS
            self.res_and_fini(res)
            return
        logger.debug("OnWeixinCallback, data:%s success, req:%s", data, self.dump_req())
        self.res_and_fini(res)

    def post(self):
        return self._deal_request()

    def get(self):
        return self._deal_request()
