# -*- coding: utf-8 -*-

import logging
import traceback
from tornado import gen
from lib import error_codes
from lib import xmq_web_handler
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class PushAndroid(xmq_web_handler.XMQWebHandler):
    executor = ThreadPoolExecutor(5)

    @gen.coroutine
    def _deal_request(self):
        logging.debug("PushAndroid, %s", self.dump_req())
        self.set_header("Content-Type", "application/json; charset=utf-8")
        res = {"status": error_codes.EC_SUCCESS}
        uids = self.get_argument("uids", "")
        if uids == "":
            res["status"] = error_codes.EC_INVALID_ARGS
        else:
            try:
                title = self.get_argument("title", "")
                desc = self.get_argument("desc", "")
                payload = self.get_argument("payload", "")
                pass_through = int(self.get_argument("pass_through", 0))
                push_type = self.get_argument("push_type", "alias")
            except Exception as e:
                logging.warning("PushAndrod, invalid args, %s %s", self.dump_req(), self.dump_exp(e))
                res["status"] = error_codes.EC_INVALID_ARGS
                self.res_and_fini(res)
                return
            try:
                yield self._send_to_android(push_type, uids, title, desc, payload, pass_through)
            except Exception as e:
                logging.warning("PushAndrod, xmpush-error, %s %s", self.dump_req(), self.dump_exp(e))
                res["status"] = error_codes.EC_FAIL
        self.res_and_fini(res)
        logger.debug("PushAndroid Done. return :%s", res)
        return

    @gen.coroutine
    def _send_to_android(self, push_type, str_uids, title, desc, payload, pass_through):
        logger.debug("_send_to_android: str_uids:%s title:%s desc:%s payload:%s",
                     str_uids, title, desc, payload)
        xiaomi_sender = self.settings["xiaomi_sender"]
        yield xiaomi_sender.send_to_android(push_type, str_uids, title, desc, payload, pass_through)

    def post(self):
        return self._deal_request()

    def get(self):
        return self._deal_request()
