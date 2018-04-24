# -*- coding: utf-8 -*-

import logging

from tornado import gen

from configs import error_codes
# from lib import sys_config
# from lib.sys_config import SysConfig
# from lib import utils
from .helper_handler import HelperHandler



class Login(HelperHandler):
    @gen.coroutine
    def _deal_request(self):
        logging.debug("OnLogin, %s", self.dump_req())
        self.set_header("Content-Type", "application/json; charset=utf-8")

        res = {"status": error_codes.EC_SUCCESS}
        auth_dao = self.settings["auth_dao"]
        user_dao = self.settings["user_dao"]
        admin_log_dao = self.settings['admin_log_dao']
        custom_headers = self.custom_headers()
        conf = self.settings["appconfig"]

        # 获取请求参数
        try:
            phone_num = self.get_argument("phone_num")
            device_type = int(self.get_argument("device_type"))
            if device_type != 1 and device_type != 2:
                self.arg_error("device_type")
            device_token = self.get_argument("device_token")
            code = self.get_argument("code")
            x_os_int=int(custom_headers.get("x_os_int",23))
        except Exception as e:
            logging.warning("OnLogin, invalid args, %s %s", self.dump_req(),
                            self.dump_exp(e))
            res["status"] = error_codes.EC_INVALID_ARGS
            self.res_and_fini(res)
            return
        #
        try:
            # 验证码则验证
            if phone_num == "13812345678" and code == "000000":
                logging.warning("apple review login ")
            elif phone_num in conf["phone_num_for_test"]:
                logging.warning("we login ")
            else:
                st = yield self.check_verify_code("OnLogin", res, 1, phone_num, code)
                if not st:
                    return res
            # 检查账号是否已经注册
            uid = yield user_dao.get_uid_by_mobile(phone_num)
            if uid is None:
                #注册
                uid = yield self.register(phone_num, x_os_int)
                if uid:
                    logging.info("add new user,mobile number:%s, uid:%d",phone_num, uid)
        # 生成token
            expire_secs = SysConfig.current().get(
                sys_config.SC_TOKEN_EXPIRE_SECS)
            token = yield auth_dao.gen_user_token(uid, True, device_type,device_token,
                expire_secs, custom_headers["platform"], custom_headers["device_model"],x_os_int)
            res["uid"] = uid
            res["token"] = token
            res["token_expire_secs"] = expire_secs

        except Exception as e:
            logging.error("OnLogin, error, %s %s", self.dump_req(),
                          self.dump_exp(e))
            res["status"] = error_codes.EC_SYS_ERROR
            return res

        # 成功
        logging.debug("OnLogin, success %s", self.dump_req())
        yield admin_log_dao.add_admin_log(uid = uid, content='Login success.Phone:%s'%(phone_num))
        return res

