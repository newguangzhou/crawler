# -*- coding: utf-8 -*-

import logging
import traceback
from tornado import gen
# from configs import error_codes, push_msg
from configs import error_codes
# from lib import sys_config
# from lib.sys_config import SysConfig
from configs import type_defines
from configs.constants import *
from utils import  utils
from .helper_handler import HelperHandler

logger = logging.getLogger(__name__)

class GetVerifyCode(HelperHandler):
    @gen.coroutine
    def _deal_request(self):
        logger.debug("OnGetVerifyCode, %s", self.dump_req())
        self.set_header("Content-Type", "application/json; charset=utf-8")
        auth_dao = self.settings["auth_dao"]
        msg_rpc = self.settings["msg_rpc"]
        res = {"status": error_codes.EC_SUCCESS}
        # 获取请求参数
        try:
            phone_num = self.get_argument("phone_num").strip()
            code_type = int(self.get_argument("type"))
            # arg1 = self.get_argument("arg1", "")  # 可变参数
            # arg2 = self.get_argument("arg2", "")  # 可变参数
            if code_type not in (1, 2, 3, 4):  # 登录/密码找回/共享宠物/绑定微信
                self.arg_error("type")
        except Exception as e:
            logger.warning("OnGetVerifyCode, invalid args, %s %s",
                            self.dump_req(), self.dump_exp(e))
            res["status"] = error_codes.EC_INVALID_ARGS
            return res
        ret = utils.is_valid_phone_num(phone_num)
        if not ret:
            res["status"] = error_codes.EC_INVALID_ARGS
            return res

        try:
            code, ec, extra = yield auth_dao.gen_user_verify_code(
                code_type, phone_num,
                Constants.get_instance().get(SC_VERIFY_CODE_LEN),
                Constants.get_instance().get(SC_VERIFY_CODE_EXPIRE_SECS),
                Constants.get_instance().get(SC_VERIFY_CODE_FREQ_SECS),
                86400, Constants.get_instance().get(
                    SC_VERIFY_CODE_FREQ_DAY_COUNT))
            if ec == error_codes.EC_FREQ_LIMIT:
                res["remain_time"] = extra
            if ec != error_codes.EC_SUCCESS:
                logger.warning("OnGetVerifyCode, gen failed, ec=%u extra=%s %s", ec, str(extra), self.dump_req())
                res["status"] = ec
                return res
            res["code"] = code
            res["next_req_interval"] = Constants.get_instance().get(SC_VERIFY_CODE_FREQ_SECS)
        except Exception as e:
            logger.error("OnGetVerifyCode, error, %s %s", self.dump_req(), self.dump_exp(e))
            res["status"] = error_codes.EC_SYS_ERROR
            return res
        # 成功
        logger.debug("OnGetVerifyCode, gen code success, code=%s %s", code, self.dump_req())
        # 发送短信
        try:
            yield msg_rpc.send_verify_code(phone_num, code, "小毛球app", code_type)
        except Exception as e:
            logger.warning("OnGetVerifyCode, send sms error, code=%s, req:%s, err:%s, traceback:%s",
                code, self.dump_req(), e, traceback.format_exc())
            res['status'] = error_codes.EC_FAIL
        return res
