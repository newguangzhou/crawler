# -*- coding: utf-8 -*-
import logging
import traceback
from tornado import gen
from configs import error_codes
from . import base_web_handler
from configs import type_defines

logger = logging.getLogger(__name__)


class SendVerify(base_web_handler.BaseWebHandler):

    @gen.coroutine
    def send_verify_code(self, code, product, phones, code_type=1):
        sender = self.settings["sms_sender"]
        ret = yield sender.send_verify(code, product, phones, code_type)
        return ret

    @gen.coroutine
    def _deal_request(self):
        logger.debug("SendVerify, %s", self.dump_req())
        self.set_header("Content-Type", "application/json; charset=utf-8")
        res = {"status": error_codes.EC_SUCCESS}
        try:
            phone_nums = self.get_argument("phones")
            code = self.get_argument("code")
            product = self.get_argument("product")
            code_type = int(self.get_argument("code_type", "1"))
        except Exception as e:
            logger.exception("OnSendSMS, invalid args, %s %s", self.dump_req(), self.dump_exp(e))
            res["status"] = error_codes.EC_INVALID_ARGS
            self.res_and_fini(res)
        else:
            ok = yield self.send_verify_code(code, product, phone_nums, code_type)
            if not ok:
                res = {"status": error_codes.EC_FAIL}
        self.res_and_fini(res)

    def post(self):
        return self._deal_request()

    def get(self):
        return self._deal_request()
