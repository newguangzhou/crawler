# -*- coding: utf-8 -*-

import tornado.web
import json
import urllib.request, urllib.parse, urllib.error
from utils import utils
import logging
import traceback

from tornado import gen

from configs import error_codes
from . import base_web_handler
logger = logging.getLogger(__name__)
COMMON_PASSWD = u"123456"

class HelperHandler(base_web_handler.BaseWebHandler):

    @gen.coroutine
    def check_verify_code(self, logprefix, res, type, phone_num, code):
        auth_dao = self.settings["auth_dao"]
        ec = yield auth_dao.check_user_verify_code(type, phone_num, code)
        if ec != error_codes.EC_SUCCESS:
            logger.warning("%s, check verify code failed, ec=%u %s",
                            logprefix, ec, self.dump_req())
            res["status"] = ec
            return False
        return True



    @gen.coroutine
    def check_token(self, logprefix, res, uid, token):
        auth_dao = self.settings["auth_dao"]
        ec, info = yield auth_dao.check_user_token(uid, token)
        if ec != error_codes.EC_SUCCESS:
            logger.warning("%s, check token failed, ec=%u %s info=%s", logprefix, ec,
                            self.dump_req(), str(info))
            res["status"] = ec
            if ec == error_codes.EC_LOGIN_IN_OTHER_PHONE:
                res["device_model"] = info["device_model"]
                res["msg"] = "您的账号已经在另一台手机登陆"
                res["date"] = utils.date2str(info["mod_date"])
            return False
        return True

    @gen.coroutine
    def register(self, phone_num, client_os_ver):
        user_dao = self.settings["user_dao"]
        uid = utils.gen_gid()
        # 添加用户信息
        try:
            yield user_dao.add_user_info(uid=uid, phone_num=phone_num, client_os_ver = client_os_ver)
        except Exception as e:
            utils.recover_log("user login error", uid=uid, phone_num=phone_num, client_os_ver = client_os_ver)
            raise e
        raise gen.Return(uid)

    @gen.coroutine
    def get_base_info(self,  uid ):
        logger.debug("get_base_info, uid:%d ", uid )
        res = {"status": error_codes.EC_SUCCESS}
        relation_dao = self.settings["relation_dao"]
        pet_dao = self.settings['pet_dao']

        try:
            res["pet_id"] = 0
            res["device_imei"] = ""
            res["wifi_bssid"] = ""
            res["wifi_ssid"] = ""
            res["has_reboot"] = 0
            res["longitude"]=-1
            res["latitude"]=-1
            res["agree_policy"]=1
            res["outdoor_on_off"]=0
            res["outdoor_wifi_bssid"]=""
            res["outdoor_wifi_ssid"]=""
            res["outdoor_in_protected"]=0
            r_info = yield relation_dao.get_default_pet(uid)
            if r_info is None:
                # 没有默认宠物， 尝试设置默认
                yield relation_dao.set_default_pet(uid)
                r_info = yield relation_dao.get_default_pet(uid)
                if r_info is None:
                    logger.warning("GetBaseInfo, uid :%d has not default pet.", uid)
                    res["status"] = error_codes.EC_PET_NOT_EXIST
                    return res

            pet_id = r_info['pet_id']
            info = yield pet_dao.get_pet_info_by_petid(pet_id,
                                                       ( "home_wifi","has_reboot","home_location","outdoor_on_off","outdoor_wifi","outdoor_in_protected",'nick'))
            if not info :
                logger.warning("GetBaseInfo in pet dao, not found,uid:%d pet_id:%d", uid, pet_id)
                res["status"] = error_codes.EC_PET_NOT_EXIST
                return res
            role = r_info['role']
            res["role"] = role
            if role == 'm':
                res['m_uid'] = r_info['uid']
                res['m_mobile'] = r_info['mobile'] 
            else:
                # 增加主账号信息
                master_info = yield relation_dao.get_relation_info(('uid','mobile'),pet_id = pet_id, role='m')
                res['m_uid'] = master_info[0]['uid']
                res['m_mobile'] = master_info[0]['mobile'] 

            res["pet_id"] = pet_id
            res["nick"] = info.get('nick','宠物')
            res["has_reboot"] = info.get("has_reboot",0)
            device_imei = r_info.get("imei", "")
            if device_imei is not None and utils.is_imei_valide(str(device_imei)):
                res["device_imei"] = device_imei
            home_wifi = info.get("home_wifi", None)
            if home_wifi is not None:
                res["wifi_bssid"] = home_wifi["wifi_bssid"]
                res["wifi_ssid"] = home_wifi["wifi_ssid"]
            home_location=info.get("home_location",None)
            if home_location is not None:
                res["longitude"]=home_location["longitude"]
                res["latitude"]=home_location["latitude"]
            res["outdoor_on_off"]=int(info.get("outdoor_on_off",0))
            outdoor_wifi=info.get("outdoor_wifi",None)
            if outdoor_wifi is not None:
                res["outdoor_wifi_bssid"] = outdoor_wifi["outdoor_wifi_bssid"]
                res["outdoor_wifi_ssid"]=outdoor_wifi["outdoor_wifi_ssid"]
            res["outdoor_in_protected"]=info.get("outdoor_in_protected",0)
            res["pet_count"] = yield relation_dao.get_pet_count(uid)
        except Exception as e:
            logger.error("get_base_info fail ,err:%s trace:%s",str(e), traceback.format_exc())
            res["status"] = error_codes.EC_SYS_ERROR
        return res


    @gen.coroutine
    def post(self):
        res = yield self._deal_request()
        if res:
            self.res_and_fini(res)

    @gen.coroutine
    def get(self):
        res = yield self._deal_request()
        if res:
            self.res_and_fini(res)
