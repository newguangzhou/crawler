# -*- coding: utf-8 -*-
import logging
import traceback
from tornado import gen
from lib import error_codes
from lib import xmq_web_handler
from lib import type_defines
from concurrent.futures import ThreadPoolExecutor
import datetime

logger = logging.getLogger(__name__)

class PushWeixin(xmq_web_handler.XMQWebHandler):
    executor = ThreadPoolExecutor(5)

    @gen.coroutine
    def _deal_request(self):
        logger.debug("PushWeixin, %s", self.dump_req())
        self.set_header("Content-Type", "application/json; charset=utf-8")
        res = {"status": error_codes.EC_SUCCESS}
        user_dao = self.settings["user_dao"]
        weixin_sender = self.settings["weixin_sender"]
        uid = int(self.get_argument("uid", "0"))
        if uid == 0:
            res["status"] = error_codes.EC_INVALID_ARGS
        else:
            try:
                data = self.get_argument("data")
                msg_type = int(self.get_argument("type"))
                msg_id = int(self.get_argument("msg_id", "0"))
            except Exception as e:
                logger.warning("PushWeixin, invalid args, %s %s", self.dump_req(), self.dump_exp(e))
                res["status"] = error_codes.EC_INVALID_ARGS
                self.res_and_fini(res)
                return
            try:
                user_info = yield user_dao.get_user_info(uid, ("wx_openid",))
                if not user_info:
                    logger.error("PushWeixin error. uid:%d has not binded weixin.", uid)
                    res["status"] = error_codes.EC_WX_NOT_BINDED
                    self.res_and_fini(res)
                    return
                openid = user_info["wx_openid"]
                ret = yield weixin_sender.push(openid=openid, desc=data, msg_type=msg_type)
                if msg_id <= 0:
                    msg_id = yield user_dao.gen_msg_sn()
                result = 0 if ret["errcode"] == 0 else -1
                yield user_dao.update_sending_msg(msg_id,
                                                  trace_id=ret["msgid"] if result == 0 else "",
                                                  uid=uid,
                                                  openid=openid,
                                                  msg_type=type_defines.MSG_TYPE_WEIXIN_PUSH,
                                                  send_time=datetime.datetime.now(),
                                                  desc=data,
                                                  result=result,
                                                  retry=1
                                                  )
            except Exception as e:
                logger.warning("PushWeixin, error, req:%s error:%s", self.dump_req(), self.dump_exp(e))
                res["status"] = error_codes.EC_FAIL
        self.res_and_fini(res)
        logger.debug("PushWeixin success. return :%s", res)
        return

    def post(self):
        return self._deal_request()

    def get(self):
        return self._deal_request()
