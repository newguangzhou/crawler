# -*- coding: utf-8 -*-
import logging
import traceback
from tornado import gen
from lib import error_codes
from lib import xmq_web_handler
from lib import type_defines
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
import datetime

logger = logging.getLogger(__name__)


class PushIOS(xmq_web_handler.XMQWebHandler):
    executor = ThreadPoolExecutor(5)

    @gen.coroutine
    def _deal_request(self):
        logger.debug("PushIOS, %s", self.dump_req())
        self.set_header("Content-Type", "application/json; charset=utf-8")
        res = {"status": error_codes.EC_SUCCESS}
        uids = self.get_argument("uids", "")
        if uids == "":
            res["status"] = error_codes.EC_INVALID_ARGS
        else:
            try:
                channel = int(self.get_argument("channel", "0"))
                payload = str(self.get_argument("payload", ""))
                extra = str(self.get_argument("extra", ""))
                push_type = self.get_argument("push_type", "alias")
            except Exception as e:
                logger.warning("PushIOS, invalid args, %s %s", self.dump_req(), self.dump_exp(e))
                res["status"] = error_codes.EC_INVALID_ARGS
                self.res_and_fini(res)
                return
            try:
                yield self._send_to_ios(push_type, uids, payload, eval(extra), channel)
            except Exception as e:
                logger.warning("PushIOS, xmpush-error, %s %s", self.dump_req(), self.dump_exp(e))
                res["status"] = error_codes.EC_FAIL
        self.res_and_fini(res)
        logger.debug("PushIOS Done. return :%s", res)
        return

    @gen.coroutine
    def _send_to_ios(self, push_type, str_uids, payload, extra, channel):
        logger.debug("_send_to_ios, uid:%s, payload:%s", str_uids, payload)
        xiaomi_sender = self.settings["xiaomi_sender"]
        yield xiaomi_sender.send_to_ios(push_type, str_uids, payload, extra, channel)
    def post(self):
        return self._deal_request()

    def get(self):
        return self._deal_request()
