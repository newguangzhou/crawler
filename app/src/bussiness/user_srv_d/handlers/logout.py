# -*- coding: utf-8 -*-

import tornado.web
import json

import logging
import traceback
from tornado.web import gen

from configs import error_codes

from .helper_handler import HelperHandler

class Logout(HelperHandler):
    @gen.coroutine
    def _deal_request(self):
        logging.debug("OnLogout, %s", self.dump_req())
        
        self.set_header("Content-Type", "application/json; charset=utf-8")
        
        auth_dao = self.settings["auth_dao"]
        admin_log_dao = self.settings['admin_log_dao']

        res = {"status":error_codes.EC_SUCCESS}
        
        # 获取请求参数
        try:
            uid = int(self.get_argument("uid"))
            token = self.get_argument("token")
        except Exception as e:
            logging.warning("OnLogout, invalid args, %s %s", self.dump_req(), self.dump_exp(e))
            res["status"] = error_codes.EC_INVALID_ARGS
            return res
        
        #
        try:
            st = yield self.check_token("OnLogout", res, uid, token)
            if not st:
                return  res
            
            yield auth_dao.delete_user_token(uid, token)
        except Exception as e:
            logging.error("OnLogout, error, %s %s", self.dump_req(), self.dump_exp(e))
            res["status"] = error_codes.EC_SYS_ERROR
            return res
            
        # 成功
        logging.debug("OnLogout, success %s",  self.dump_req())
        yield admin_log_dao.add_admin_log(uid = uid, content='Logout success.')
        return res

