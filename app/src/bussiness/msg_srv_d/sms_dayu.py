# -*- coding: utf-8 -*-
"""
使用dayu的短信发送服务
"""
import logging
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from tornado.ioloop import IOLoop
from top import api
import functools
import top
import sys

logger = logging.getLogger(__name__)


class DayuSmsSender:
    executor = ThreadPoolExecutor(5)

    def __init__(self, appkey="23566149", secrt="f95d87510975317c9539d858c010f5a0"):
        self.__appkey = appkey
        self.__secrt = secrt

    @run_on_executor
    def send_verify(self, code, product, phones, code_type=1):
        logger.debug("code:%s product:%s phones:%s code_type:%d", code, product, phones, code_type)
        req = api.AlibabaAliqinFcSmsNumSendRequest()
        req.set_app_info(top.appinfo(self.__appkey, self.__secrt))
        req.extend = ""
        req.sms_type = "normal"
        if code_type == 1:
            req.sms_free_sign_name = "小毛球"
            req.sms_param = "{code:'%s', product:'%s'}" % (code, product)
            req.rec_num = phones
            req.sms_template_code = "SMS_91765057"
        elif code_type == 4:
            req.sms_free_sign_name = "小毛球"
            req.sms_param = "{code:'%s'}" % code
            req.rec_num = phones
            req.sms_template_code = "SMS_129749032"
        try:
            req.getResponse()
            return True
        except Exception as e:
            logger.exception(e)
            return False

    @run_on_executor
    def send_sms_message(self, template_code, message, phone):
        logger.debug("message:%s, phone:%s", message, phone)
        try:
            req = api.AlibabaAliqinFcSmsNumSendRequest()
            req.set_app_info(top.appinfo(self.__appkey, self.__secrt))
            req.extend = ""
            req.sms_type = "normal"
            req.sms_free_sign_name = "小毛球"
            req.rec_num = phone
            req.sms_param = message
            req.sms_template_code = template_code
            resp = req.getResponse()
        except Exception as e:
            logger.error("send sms phone:%s message:%s fail. err:%s", phone, message, e)
            return None
        logger.debug("send sms resp:%s", resp)
        return resp.get("alibaba_aliqin_fc_sms_num_send_response", None)

    @run_on_executor
    def get_send_sms_result(self, mobile, date, biz_id):
        logger.debug("get_send_sms_result, biz_id:%s", biz_id)
        try:
            req = api.AlibabaAliqinFcSmsNumQueryRequest()
            req.set_app_info(top.appinfo(self.__appkey, self.__secrt))
            req.biz_id = biz_id
            req.rec_num = mobile
            req.query_date = date
            req.current_page = 1
            req.page_size = 10
            resp = req.getResponse()
            logger.debug("result: biz_id:%s result:%s", biz_id, resp)
            return resp.get("alibaba_aliqin_fc_sms_num_query_response", None)
        except Exception as e:
            logger.warning("getResponse exception:%s", e)
            return 1 # 未知状态=1


if __name__ == '__main__':
    # send_verify("123222", "小试试", 18666023586)
    sender = DayuSmsSender()
    # func = functools.partial(sender.send_sms_message, "SMS_132391427", {"message":"毛毛"}, 15920950147)
    print("argv=%s", sys.argv)
    func = functools.partial(sender.get_send_sms_result, sys.argv[1], sys.argv[2], sys.argv[3])
    IOLoop.current().run_sync(func)
