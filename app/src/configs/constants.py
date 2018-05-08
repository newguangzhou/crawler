# -*- coding: utf-8 -*-

import json
import logging

from tornado import ioloop, gen
logger = logging.getLogger(__name__)

DEFAULT_CATEGORY = 1  # 默认的系统配置类别
SC_FILE_BASE_URL = 1  # 系统文件基础url
SC_VERIFY_CODE_LEN = 2  # 验证码长度
SC_VERIFY_CODE_FREQ_SECS = 3  # 验证码获取间隔秒数
SC_VERIFY_CODE_FREQ_DAY_COUNT = 4  # 用户每天获取验证码的最大次数, 如果为0则不限制
SC_VERIFY_CODE_EXPIRE_SECS = 5  # 验证码过期秒数
SC_TOKEN_EXPIRE_SECS = 6  # token过期秒数
SC_LOGIN_FREQ_INTERVAL_SECS = 7  # 连续登录失败情况下的频率检查间隔
SC_LOGIN_FREQ_INTERVAL_FAILED_COUNT = 8  # 连续登录失败情况下最大的失败次数
SC_VERIFY_CODE_REGISTER_SMS_FORMAT = 9  # 注册验证码短信格式
SC_VERIFY_CODE_LOGIN_SMS_FORMAT = 10  # 登录验证码短信格式
SC_VERIFY_CODE_RESET_PASSWD_SMS_FORMAT = 11  # 重置密码验证码短信格式
SC_GID_RPC_URL = 12  # GID远程服务的url
SC_AMOUNT_TO_JIFEN_UNIT = 13  # 消费金额到积分的兑换单位
SC_UPLOAD_IMAGE_TYPES = 14  # 支持的上传的图片类型
SC_USER_LOGO_MAX_SIZE = 15  # 用户logo的图片的最大大小
SC_MSG_RPC_URL = 16  # 消息网关远程服务的url

SC_AC_MAX_TAKE_COUNT_RULE_DESC_FMT = 17  # 活动每个用户领取最多领取次数规则描述格式
SC_AC_MAX_USE_COUNT_RULE_DESC_FMT = 18  # 每个用户每次最多使用的数量规则描述格式
SC_SALE_AMOUNT_LOWER_BOUND_RULE_DESC_FMT = 19  # 使用活动时消费金额必须满足指定的下限规则描述格式
SC_SHARE_WITH_OTHERS_RULE_DESC_FMT = 20  # 是否与其他优惠活动同享规则描述格式
SC_AC_ONLY_NEW_USER_RULE_DESC_FMT = 21  # 是否仅限新用户领取规则描述格式
SC_AC_ONLY_MEMBER_RULE_DESC_FMT = 22  # 是否仅限店铺会员参与
SC_TERMINAL_RPC_URL = 30
SC_SIM_CARD_EXPIRE_DAYS = 31 #sim card 默认过期时间,天数


class SysConfigException(Exception):
    def __init__(self, msg, *args):
        self._msg = msg % tuple(args)

    def __str__(self):
        return self._msg


_CONFIG_ITEMS = {  # Key is item key, value is (类型，默认值，验证器)
    SC_FILE_BASE_URL: (str, "http://120.24.152.121:9700/file/get", None),
    SC_VERIFY_CODE_LEN: (int, 6, None),
    SC_VERIFY_CODE_FREQ_SECS: (int, 60, None),
    SC_VERIFY_CODE_FREQ_DAY_COUNT: (int, 20, None),
    SC_VERIFY_CODE_EXPIRE_SECS: (int, 1800, None),
    SC_TOKEN_EXPIRE_SECS: (int, 17280000, None),
    SC_LOGIN_FREQ_INTERVAL_SECS: (int, 120, None),
    SC_LOGIN_FREQ_INTERVAL_FAILED_COUNT: (int, 4, None),
    SC_VERIFY_CODE_REGISTER_SMS_FORMAT:
    (str, "【小毛球】注册验证码：%s，五分钟内输入有效，谢谢！", None),
    SC_VERIFY_CODE_LOGIN_SMS_FORMAT: (str, "【小毛球】尊敬的用户您好，您的登录验证码为%s", None),
    SC_VERIFY_CODE_RESET_PASSWD_SMS_FORMAT:
    (str, "【小毛球】找回密码验证码：%s，五分钟内输入有效，请勿转给他人！", None),
    SC_GID_RPC_URL: (str, "http://100.98.6.55:8080/gid/alloc", None),
    SC_AMOUNT_TO_JIFEN_UNIT: (int, 1, None),
    SC_UPLOAD_IMAGE_TYPES: (list, [".jpg", ".jpeg", ".png"], None),
    SC_USER_LOGO_MAX_SIZE: (int, 1024 * 1024, None),
    SC_MSG_RPC_URL: (str, "http://127.0.0.1:9200", None),
    SC_AC_MAX_TAKE_COUNT_RULE_DESC_FMT: (str, "每个用户最多领取%u个", None),
    SC_AC_MAX_USE_COUNT_RULE_DESC_FMT: (str, "每个用户每次最多可使用%u个", None),
    SC_SALE_AMOUNT_LOWER_BOUND_RULE_DESC_FMT: (str, "消费满%.1f元才能使用", None),
    SC_SHARE_WITH_OTHERS_RULE_DESC_FMT: (str, "%s与其他优惠同享", None),
    SC_AC_ONLY_NEW_USER_RULE_DESC_FMT: (str, "%s", None),
    SC_AC_ONLY_MEMBER_RULE_DESC_FMT: (str, "%s", None),
    SC_TERMINAL_RPC_URL: (str, "http://127.0.0.1:5052", None),
    SC_SIM_CARD_EXPIRE_DAYS: (int, 180, None),
}

class Constants:
    _current_inst = None

    @staticmethod
    def _local_debug_hack():
        _CONFIG_ITEMS[SC_FILE_BASE_URL] = (
            str, "http://120.24.152.121:9700/file/get", None)
        _CONFIG_ITEMS[SC_GID_RPC_URL] = (
            str, "http://127.0.0.1:9800/gid/alloc", None)
        _CONFIG_ITEMS[SC_MSG_RPC_URL] = (str, "http://127.0.0.1:9200", None)
        _CONFIG_ITEMS[SC_TERMINAL_RPC_URL] = (str, "http://127.0.0.1:5052",
                                              None)

    # 47.93.249.1
    @staticmethod
    def _test_debug_hack():
        _CONFIG_ITEMS[SC_FILE_BASE_URL] = (
            str, "http://120.24.152.121:9700/file/get", None)
        _CONFIG_ITEMS[SC_GID_RPC_URL] = (
            str, "http://127.0.0.1:9800/gid/alloc", None)
        _CONFIG_ITEMS[SC_MSG_RPC_URL] = (str, "http://127.0.0.1:9200", None)
        _CONFIG_ITEMS[SC_TERMINAL_RPC_URL] = (str, "http://127.0.0.1:5052",
                                              None)

    @staticmethod
    def _disable_debug_hack():
        _CONFIG_ITEMS[SC_FILE_BASE_URL] = (

            str, "http://120.24.152.121:9700/file/get", None)
        _CONFIG_ITEMS[SC_GID_RPC_URL] = (
            str, "http://127.0.0.1:9800/gid/alloc", None)
        _CONFIG_ITEMS[SC_MSG_RPC_URL] = (str, "http://127.0.0.1:9200", None)
        _CONFIG_ITEMS[SC_TERMINAL_RPC_URL] = (str, "http://127.0.0.1:5052",
                                              None)

    @staticmethod
    def new():
        # inst = Constants()

        # debug_mode = 1
        # if kwargs.has_key("debug_mode"):
        #     debug_mode = kwargs["debug_mode"]
        #
        # if debug_mode == 1:
        #     SysConfig._local_debug_hack()
        # elif debug_mode == 2:
        #     SysConfig._test_debug_hack()
        # elif debug_mode == 0:
        #     SysConfig._disable_debug_hack()

        if Constants._current_inst is None:
            Constants._current_inst = Constants()

        return Constants._current_inst

    @staticmethod
    def get_instance():
        return Constants._current_inst

    def __init__(self, **kwargs):
        pass

    def get(self, item):
        # if self._cache is None:
        #     raise SysConfigException("Not opened")

        if item not in _CONFIG_ITEMS:
            raise SysConfigException("Unkown sys config item \"%u\"", item)

        # valtype, defval, validator = _CONFIG_ITEMS[item]
        logger.debug("test-item, %s", _CONFIG_ITEMS[item])
        # if valtype == list or valtype == dict or valtype == tuple:
        #     ret = json.loads(_CONFIG_ITEMS[item])
        # else:
        #     raise SysConfigException("Not opened")
        return _CONFIG_ITEMS[item][1]

    def gen_file_url(self, file_category, file_id):
        return "%s?type=%u&file_id=%s" % (self.get(SC_FILE_BASE_URL),
                                          file_category, file_id)


if __name__ == "__main__":
    import sys
    sys.path.append("../")

    import configs.mongo_config
    """
    @gen.coroutine
    def _main():
        mongo_conf = configs.mongo_config.MongoConfig()
        sysconf = SysConfig.new(mongo_meta = mongo_conf.global_mongo_meta)
    
        val = yield sysconf.get(SC_FILE_BASE_URL)
        print val
        
        val = yield sysconf.get(SC_UPLOAD_IMAGE_TYPES)
        print val
        yield sysconf.set(SC_UPLOAD_IMAGE_TYPES, [".gif"])
        val = yield sysconf.get(SC_UPLOAD_IMAGE_TYPES)
        print val
    
    ioloop.IOLoop.current().run_sync(_main)
    """
