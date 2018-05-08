# -*- coding: utf-8 -*-
import logging
import traceback
import datetime
from tornado.web import asynchronous
from tornado import gen
from configs import error_codes
from . import base_web_handler
from configs import type_defines


def share_pet_fun(msg):
    js = eval(msg)
    return "小毛球正在邀请您成为宠物%s的子账号，如接受，请将安全码%s转告用户%s." %(js['pet'], js['code'], js['mob'])

def warn_before_deadline(msg):
    js = eval(msg)
    return "%s的追踪器（IMEI：%s）内置专用sim卡服务还有%d天过期，为了您宠物的安全，请及时充值。"% (js['nick'], js['imei'], js['days'])

def warn_deadline(msg):
    js = eval(msg)
    return "%s的追踪器（IMEI：%s）内置专用sim卡服务已欠费%d天，为了您宠物的安全，请及时充值。"% (js['nick'], js['imei'], js['days'])

def warn_stop_service(msg):
    js = eval(msg)
    return "%s的追踪器（IMEI：%s）内置专用sim卡将于%d天后停机，为了您宠物的安全，请及时充值。停机6个月后，sim卡将自动销户，追踪器再也无法使用。"% (js['nick'], js['imei'], js['days'])

def warn_unregist(msg):
    js = eval(msg)
    return "%s的追踪器（IMEI：%s）内置专用sim卡将于%d天后销户，销户后追踪器再也无法使用。为了您宠物的安全，请及时充值。" % (js['pet'], js['imei'], js['days'])

sms_template = {
    type_defines.MSG_TMPL_IN_HOME: lambda message: "%s已安全到家。" % message,
    type_defines.MSG_TMPL_OUT_HOME: lambda message: "%s可能离家，请确认安全。" % message,
    type_defines.MSG_TMPL_LOW_BATTERY: lambda message: "%s的追踪器电量低，请及时充电！" % message,
    type_defines.MSG_TMPL_SUPER_LOW_BATTERY: lambda message: "%s的追踪器电量超低，请及时充电！" % message,
    type_defines.MSG_TMPL_IN_PROTECTED: lambda message: "%s回到户外保护范围。" % message,
    type_defines.MSG_TMPL_OUT_PROTECTED: lambda message: "%s脱离户外保护范围，请注意安全。" % message,
    type_defines.MSG_TMPL_WARN_BEFORE_DEADLINE: warn_before_deadline,
    type_defines.MSG_TMPL_WARN_DEADLINE: warn_deadline,
    type_defines.MSG_TMPL_WARN_STOP_SERVICE: warn_stop_service,
    type_defines.MSG_TMPL_WARN_UNREGIST: warn_unregist,
    type_defines.MSG_TMPL_SHARE_PET: share_pet_fun
    }


class SendSMS(base_web_handler.BaseWebHandler):

    @asynchronous
    @gen.coroutine
    def _deal_request(self):
        logging.debug("OnSendSMS, %s", self.dump_req())
        self.set_header("Content-Type", "application/json; charset=utf-8")
        res = {"status":error_codes.EC_SUCCESS}
        sms_sender = self.settings["sms_sender"]
        user_dao = self.settings["user_dao"]
        # 获取请求参数
        try:
            phone_num = self.get_argument("phone_num")
            sms_type = self.get_argument("sms_type")
            sms = self.get_argument("sms")
            sms = self.decode_argument(sms)
        except Exception as e:
            logging.warning("OnSendSMS, invalid args, %s", self.dump_req())
            res["status"] = error_codes.EC_INVALID_ARGS
            self.res_and_fini(res)
            return
        recv = yield sms_sender.send_sms_message(sms_type, sms, phone_num)
        # 发送成功
        logging.debug("OnSendSMS, req:%s res:%s", self.dump_req(), res)
        self.res_and_fini(res)
        
    def post(self):
        return self._deal_request()
    
    def get(self):
        return self._deal_request()
    
    
