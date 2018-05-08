# -*- coding: utf-8 -*-

import json
import traceback
import logging
from configs import error_codes
import tornado.web
from configs import type_defines
logger = logging.getLogger(__name__)


class BaseInvalidArgumentException(Exception):
    def __init__(self, message, *args):
        self._msg = message % tuple(args)

    def __str__(self):
        return self._msg


class BaseWebHandler(tornado.web.RequestHandler):
    def dump_req(self):
        args_str = ""
        n = len(self.request.arguments)
        for i in range(0, n):
            k, v = list(self.request.arguments.items())[i]
            args_str += str(k) + "="
            if len(v) > 0:
                try:
                    if k != "passwd" and k != "pass" and k != "password":
                        args_str += self.decode_argument(v[0])
                    else:
                        args_str += "******"
                except Exception as e:
                    logging.warning(
                        "Get request argument string error, path=\"%s\" argument=\"%s\" error=\"%s\" trace=\"%s\"",
                        self.request.path, k, str(e), traceback.format_exc())
            else:
                args_str += ""
            if i != n - 1:
                args_str += ","
        return "args=\"%s\" remote_ip=%s" % (args_str, self.request.remote_ip)

    @classmethod
    def arg_error(cls, name, msg=None, *args):
        expmsg = "Invalid argument \"%s\"" % (name, )
        if msg:
            tmp = msg % tuple(args)
            expmsg += ",%s" % (tmp, )
        raise BaseInvalidArgumentException(expmsg)

    @classmethod
    def dump_exp(cls, e):
        return "exp=\"%s\" trace=\"%s\"" % (str(e), traceback.format_exc())

    def res_and_fini(self, res):
        data = json.dumps(res, ensure_ascii=False).encode('utf8')
        self.write(data)
        self.finish()
        logger.debug("res_and_fini:%s", data)

    def get_str_arg(self, arg):
        tmp = self.get_argument(arg, "")
        if tmp == "":
            return tmp
        else:
            return self.decode_argument(tmp).encode("utf8")

    def custom_headers(self):
        ret = {}
        os = self.request.headers.get(HTTP_HD_OS, "")
        if os.startswith(HTTP_HD_ANDROID_START_STRING):
            platform = PLATFORM_ANDROID
        else:
            platform = PLATFORM_IOS
        ret["x_os_int"] = self.request.headers.get(HTTP_HD_OS_INT, "23")
        ret["platform"] = platform
        ret["app_version"] = self.request.headers.get(HTTP_HD_APPVERSION, "")
        ret["device_model"] = self.request.headers.get(HTTP_HD_DEVICE_MODEL, "")
        return ret
