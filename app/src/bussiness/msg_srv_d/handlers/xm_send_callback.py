# -*- coding: utf-8 -*-


import logging
import traceback
import json
from tornado.web import asynchronous
from tornado import gen
from lib import error_codes, type_defines
from lib import xmq_web_handler

logger = logging.getLogger(__name__)
class XMSendCallback(xmq_web_handler.XMQWebHandler):
    @asynchronous
    @gen.coroutine
    def _deal_request(self):
        logger.debug("OnXMCallback, %s", self.dump_req())
        self.set_header("Content-Type", "application/json; charset=utf-8")
        res = {"status": error_codes.EC_SUCCESS}
        # 获取请求参数
        try:
            data = self.get_argument("data")
            args = json.loads(data)
            sending_mgr = self.settings["sending_mgr"]
            for k, v in args.items():
                msg_id = int(v['param'])
                yield sending_mgr.finish_sending_task(msg_id, type_defines.MSG_TYPE_APP_PUSH,
                                                      recv_result=type_defines.MSG_RESULT_RECV_SUCCESS)
                logger.debug("OnXMCallback msg_id: %d", msg_id)
        except Exception as e:
            logger.warning("OnXMCallback, invalid args, %s, %s error:%s", self.dump_req(), traceback.format_exc(), e)
            res["status"] = error_codes.EC_INVALID_ARGS
            self.res_and_fini(res)
            return 
        logger.debug("OnXMCallback, arg type:%s args:%s success, req:%s", type(args), args, self.dump_req())
        self.res_and_fini(res)
        
    def post(self):
        return self._deal_request()
    
    def get(self):
        return self._deal_request()
