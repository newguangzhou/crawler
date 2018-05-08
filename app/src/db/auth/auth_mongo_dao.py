# -*- coding: utf-8 -*-

import datetime
import time
import random
import hashlib

from tornado import gen

from db.auth import auth_mongo_defines as auth_def
from utils import base_utils

import pymongo

from db.mongo_dao_base import MongoDAOBase
from configs import error_codes

from configs import type_defines

_OLD_USER_PASSWD_EXTRA_KEY = "k|~58j9t*MzTC2G_=}/(l)$nBsNx&Ub;@i1g0Ymc"

"""
验证码类型
"""
VERIFY_CODE_TYPES = (
    1,  #登陆验证码
    2,  #密码找回验证码
    3,  #共享宠物验证码
    4,  # 微信绑定
)

class AuthMongoDAOException(Exception):
    def __init__(self, message, *args):
        self._msg = message % tuple(args)

    def __str__(self):
        return self._msg


class AuthMongoDAO(MongoDAOBase):
    def __init__(self, *args, **kwargs):
        MongoDAOBase.__init__(self, *args, **kwargs)

    def _gen_hash_passwd(self, mobile_num, passwd):
        sha1 = hashlib.sha1()
        sha1.update(passwd.encode('utf-8'))
        user_hashpasswd = sha1.hexdigest()

        salt = "%s%u%u" % (mobile_num, int(time.time() * 10000),
                           random.randint(0, 999999999))
        sha1 = hashlib.sha1()
        sha1.update(salt.encode('utf-8'))
        salt_hash = sha1.hexdigest()

        salt_passwd = user_hashpasswd + salt_hash
        sha1 = hashlib.sha1()
        sha1.update(salt_passwd.encode('utf-8'))
        salt_hashpasswd = sha1.hexdigest()

        return (salt_hashpasswd, salt_hash)

    def _check_passwd(self, upasswd, hashpass, salt):
        sha1 = hashlib.sha1()
        sha1.update(upasswd)
        uhashpasswd = sha1.hexdigest()

        salt_passwd = uhashpasswd + salt
        sha1 = hashlib.sha1()
        sha1.update(salt_passwd)

        return hashpass == sha1.hexdigest()

    def _check_passwd_old_user(self, upasswd, hashpass):
        sha1 = hashlib.sha1()
        sha1.update(upasswd)

        md5 = hashlib.md5()
        md5.update(sha1.hexdigest() + _OLD_USER_PASSWD_EXTRA_KEY)

        return hashpass == md5.hexdigest()

    def _new_verify_code(self, len):
        ret = ""
        for i in range(0, len):
            ret += str(random.randint(0, 9))
        return ret



    @gen.coroutine
    def get_auth_device_info(self,  auth_id):
        def _callback(mongo_client, **kwargs):
            tb = mongo_client[auth_def.AUTH_DATABASE][auth_def.AUTH_STATUS_TB]

            cursor = tb.find({"auth_type": type_defines.USER_AUTH,
                              "auth_id": auth_id}, {"_id": 0,
                                                    "device_type": 1,
                                                    "device_model": 1,
                                                    "device_token": 1},sort=[("mod_date",pymongo.DESCENDING)]).limit(1)
            if cursor.count() <= 0:
                return None
            return cursor[0]

        ret = yield self.submit(_callback)
        raise gen.Return(ret)

    @gen.coroutine
    def get_login_device_type(self, uid):
        auth_info = yield self.get_auth_device_info(uid)
        if not auth_info:
            return None
        device_model = auth_info["device_model"]
        if device_model == "iPhone" or device_model == "iPad":
            return type_defines.PLATFORM_IOS
        else:
            return type_defines.PLATFORM_ANDROID



    def gen_token(self, type, auth_id, multi_login, device_type, device_token,
                  expire_times, platform, device_model,device_os_int):
        def _callback(mongo_client, **kwargs):
            tb = mongo_client[auth_def.AUTH_DATABASE][auth_def.AUTH_STATUS_TB]

            cond = {"auth_type": type, "auth_id": auth_id}
            count = tb.count(cond)

            timestamp = int(time.time() * 10000)
            seek1 = random.randint(0, 999999999)
            seek2 = random.randint(999999999, 2000000000)
            seek3 = random.randint(2000000000, 3000000000)
            seek4 = random.randint(3000000000, 4000000000)
            orig_token = "%s%u%s%u%u%u%u%s%u" % (
                str(auth_id), timestamp, str(device_type), seek1, seek2, seek3,
                seek4, str(device_token), count + 1)
            orig_token = orig_token.encode('utf-8')
            sha1 = hashlib.sha1()
            sha1.update(orig_token)
            token = sha1.hexdigest()

            row = auth_def.new_auth_status_row()
            row["auth_type"] = type
            row["auth_id"] = auth_id
            row["token"] = token
            row["device_type"] = device_type
            row["device_token"] = device_token
            row["expire_times"] = expire_times
            row["platform"] = platform
            row["device_model"] = device_model
            row["device_os_int"]=device_os_int

            if not multi_login:
                tb.delete_many(cond)

            tb.insert_one(row)

            return token

        return self.submit(_callback)

    """
    生成用户token
    """

    def gen_user_token(self, uid, multi_login, device_type, device_token,
                       expire_times, platform, device_model,device_os_int):
        return self.gen_token(type_defines.USER_AUTH, uid, multi_login,
                              device_type, device_token, expire_times,
                              platform, device_model,device_os_int)

    # def get_cur_login_info(self, type, auth_id):
    #    info = {}
    #    tb = mongo_client[auth_def.AUTH_DATABASE][auth_def.AUTH_STATUS_TB]
    #    return tb.find_one({"auth_type": type,
    #                        "auth_id": auth_id}, sort=[("add_date", pymongo.DESCENDING)])

    def check_token(self, type, auth_id, token):
        def _callback(mongo_client, **kwargs):
            # 检查token状态
            ec = error_codes.EC_SUCCESS
            info = {}
            tb = mongo_client[auth_def.AUTH_DATABASE][auth_def.AUTH_STATUS_TB]

            info = tb.find_one({"auth_type": type,
                                "auth_id": auth_id},
                               sort=[("add_date", pymongo.DESCENDING)])

            if info is None:
                ec = error_codes.EC_INVALID_TOKEN
            else:
                if info["state"] == 0:
                    ec = error_codes.EC_INVALID_TOKEN
                elif info["token"] != token:
                        ec = error_codes.EC_LOGIN_IN_OTHER_PHONE
                elif info["expire_times"] != 0:
                    tm = base_utils.date2int(info["mod_date"]) + info[
                        "expire_times"]
                    cur_tm = int(time.time())
                    if cur_tm >= tm:  # 已经过期
                        ec = error_codes.EC_TOKEN_EXPIRED
            return ec, info

        return self.submit(_callback)

    """
    检查用户token
    """

    def check_user_token(self, uid, token):
        return self.check_token(type_defines.USER_AUTH, uid, token)

    @gen.coroutine
    def delete_token(self, type, auth_id, token):
        def _callback(mongo_client, **kwargs):
            tb = mongo_client[auth_def.AUTH_DATABASE][auth_def.AUTH_STATUS_TB]
            tb.delete_one({"auth_type": type,
                           "auth_id": auth_id,
                           "token": token})

        yield self.submit(_callback)

    """
    删除用户token
    """

    @gen.coroutine
    def delete_user_token(self, uid, token):
        yield self.delete_token(type_defines.USER_AUTH, uid, token)

    @gen.coroutine
    def delete_all_tokens(self, type, auth_id):
        def _callback(mongo_client, **kwargs):
            tb = mongo_client[auth_def.AUTH_DATABASE][auth_def.AUTH_STATUS_TB]
            tb.delete_many({"auth_type": type, "auth_id": auth_id})

        yield self.submit(_callback)

    @gen.coroutine
    def delete_user_all_tokens(self, uid):
        yield self.delete_all_tokens(type_defines.USER_AUTH, uid)

    """
    len  验证码的长度
    expire_times 过期时间以秒为单位
    interval   距离上一次请求的必须的间隔时间，以秒为单位
    freq_check_interval 频率检查间隔
    freq_limit_count 在一个频率检查间隔内的最大请求数量
    """

    @gen.coroutine
    def gen_verify_code(self, auth_type, type, mobile_num, len, expire_times,
                        interval, freq_check_interval, freq_limit_count):
        if type not in VERIFY_CODE_TYPES:
            raise AuthMongoDAOException("Unknown verify code type, type=%u",
                                        type)

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[auth_def.AUTH_DATABASE][
                auth_def.VERIFY_CODE_STATUS_TB]
            cond = {"auth_type": auth_type,
                    "type": type,
                    "mobile_num": mobile_num}
            info = None
            cursor = tb.find(cond)
            if cursor.count() > 0:
                info = cursor[0]
            if info is None:  # 不存在则创建
                code = self._new_verify_code(len)
                row = auth_def.new_verify_code_status_row()
                row["auth_type"] = auth_type
                row["type"] = type
                row["mobile_num"] = mobile_num
                row["code"] = code
                row["freq_counter"] = 1
                row["expire_times"] = expire_times
                tb.insert_one(row)
                return (code, error_codes.EC_SUCCESS, None)

# 首先检查距离上一次请求的时间间隔
            pre_tm = base_utils.date2int(info["mod_date"])
            cur_tm = int(time.time())
            if cur_tm - pre_tm <= interval:
                return (None, error_codes.EC_FREQ_LIMIT,
                        pre_tm + interval - cur_tm)

            # 检查频率
            freq_begin_tm = info["freq_begin_tm"]
            if cur_tm > freq_begin_tm + freq_check_interval:  # 频率定时器已经过期
                code = self._new_verify_code(len)
                tb.update_one(cond, {"$set": {"code": code,
                                              "expire_times": expire_times,
                                              "mod_date":
                                              datetime.datetime.today(),
                                              "freq_begin_tm": cur_tm,
                                              "freq_counter": 1}})
                return (code, error_codes.EC_SUCCESS, None)
            elif info["freq_counter"] >= freq_limit_count:  # 超出频率限制
                return (None, error_codes.EC_FREQ_LIMIT,
                        freq_begin_tm + freq_check_interval - cur_tm)
            else:  # 正常请求
                code = self._new_verify_code(len)
                tb.update_one(cond, {"$inc": {"freq_counter": 1},
                                     "$set": {"code": code,
                                              "expire_times": expire_times,
                                              "mod_date":
                                              datetime.datetime.today()}})
                return (code, error_codes.EC_SUCCESS, None)

        ret = yield self.submit(_callback)
        raise gen.Return(ret)

    @gen.coroutine
    def gen_user_verify_code(self, type, mobile_num, len, expire_times,
                             interval, freq_check_interval, freq_limit_count):
        ret = yield self.gen_verify_code(
            type_defines.USER_AUTH, type, mobile_num, len, expire_times,
            interval, freq_check_interval, freq_limit_count)
        raise gen.Return(ret)

    @gen.coroutine
    def check_verify_code(self, auth_type, type, mobile_num, verify_code):
        if type not in VERIFY_CODE_TYPES:
            raise AuthMongoDAOException("Unknown verify code type, type=%u",
                                        type)

        def _callback(mongo_client, **kwargs):
            tb = mongo_client[auth_def.AUTH_DATABASE][
                auth_def.VERIFY_CODE_STATUS_TB]

            cond = {"auth_type": auth_type,
                    "type": type,
                    "mobile_num": mobile_num}
            info = None
            cursor = tb.find(cond)
            if cursor.count() > 0:
                info = cursor[0]
            else:
                return error_codes.EC_INVALID_VERIFY_CODE

            if info["code"] != verify_code:
                return error_codes.EC_INVALID_VERIFY_CODE

            tm = base_utils.date2int(info["mod_date"])
            cur_tm = int(time.time())
            if cur_tm > tm + info["expire_times"]:
                return error_codes.EC_VERIFY_CODE_EXPIRED

            return error_codes.EC_SUCCESS

        ret = yield self.submit(_callback)
        raise gen.Return(ret)

    @gen.coroutine
    def check_user_verify_code(self, type, mobile_num, verify_code):
        ret = yield self.check_verify_code(type_defines.USER_AUTH, type,
                                           mobile_num, verify_code)
        raise gen.Return(ret)
