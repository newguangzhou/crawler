# -*- coding: utf-8 -*-

import urllib.request, urllib.parse, urllib.error
import time
import logging
import uuid
import json
import traceback

from tornado import gen
from tornado.httpclient import AsyncHTTPClient

from configs import type_defines
from configs import error_codes


class MsgRPCException(Exception):
    def __init__(self, message, *args):
        self._message = message % tuple(args)

    def __str__(self):
        return self._message


class MsgRPC:
    """
    MSGRPC 机制只提供发送消息接口，
    不提供重试机制，
    不提供业务控制逻辑（例如不管设备服务是否到期，只要调用这个接口就肯定会发送)

    需要业务控制逻辑请用mongodb 的消息队列接口 push_msg()
    """
    def __init__(self, msg_url):
        self._apis = {
            "send_sms": "%s/msg/send_sms" % (msg_url, ),
            "send_verify_code": "%s/msg/send_verify_code" % (msg_url, ),
            "push": "%s/msg/push" % (msg_url, ),
            "push_all": "%s/msg/push_all" % (msg_url, ),
            "push_android": "%s/msg/push_android" % (msg_url, ),
            "push_ios": "%s/msg/push_ios" % (msg_url, ),
            "push_weixin": "%s/msg/push_weixin" % (msg_url, )
        }
        #self._service_name = service_name

    @gen.coroutine
    def call(self, api, **args):
        body = args
        #print self._apis[api]
        http_client = AsyncHTTPClient()
        res = yield http_client.fetch(self._apis[api],
                                      method="POST",
                                      body=urllib.parse.urlencode(body),
                                      connect_timeout=10,
                                      request_timeout=10)
        res = json.loads(str(res.body, encoding="utf-8"))
        if res["status"] != error_codes.EC_SUCCESS:
            raise MsgRPCException("Call error, status=%u", res["status"])
        raise gen.Return(res)

    @gen.coroutine
    def send_sms(self, sms_type, phone_num, sms):
        ret = yield self.call("send_sms", sms_type=sms_type, phone_num=phone_num, sms=sms)
        raise gen.Return(ret)

    @gen.coroutine
    def send_verify_code(self, phones, code, product, code_type=1):
        ret = yield self.call("send_verify_code",
                              phones=phones,
                              code=code,
                              product=product,
                              code_type=code_type)
        raise gen.Return(ret)

    @gen.coroutine
    def push_weixin(self, **args):
        ret = yield self.call("push_weixin", **args)
        raise gen.Return(ret)

    # default is alias
    @gen.coroutine
    def push_android(self, **args):
        args["push_type"] = "alias"
        ret = yield self.call("push_android", **args)
        raise gen.Return(ret)
    # defalut is alias

    @gen.coroutine
    def push_ios(self, **args):
        args["push_type"] = "alias"
        ret = yield self.call("push_ios", **args)
        raise gen.Return(ret)

    # default is alias
    @gen.coroutine
    def push_android_useraccount(self, **args):
        args["push_type"] = "user_account"
        ret = yield self.call("push_android", **args)
        raise gen.Return(ret)

    # defalut is alias
    @gen.coroutine
    def push_ios_useraccount(self, **args):
        args["push_type"] = "user_account"
        ret=yield self.call("push_ios", **args)
        raise gen.Return(ret)

    @gen.coroutine
    def push(self, uid, title, desc):
        ret = yield self.call("push", uid=uid, title=title, desc=desc)
        raise gen.Return(ret)

    @gen.coroutine
    def push_all(self, title, desc, extras):
        ret = yield self.call("push_all", title=title, desc=desc, data = extras)
        raise gen.Return(ret)

    def gen_push_data(self, type, **extras):
        ret = {"type": type}
        for (k, v) in list(extras.items()):
            ret[k] = v
        return json.dumps(ret)
