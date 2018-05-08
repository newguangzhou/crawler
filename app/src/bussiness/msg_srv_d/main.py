# -*- coding: utf-8 -*-

import sys
import importlib
sys.path.append("../../")
importlib.reload(sys)
import logging
from handlers import send_sms, send_verify_code
from tornado import ioloop
from tornado.web import Application
from tornado.options import define,options
from sms_dayu import DayuSmsSender
from utils import base_utils

define("port",default=9200,help="run tornado service",type=int)


proctitle = "msg_srv_d"


def main():
    base_utils.init_service(proctitle, logging.DEBUG)
    # xiaomi_sender = MiSender(proc_conf["mipush_appsecret_android"],
    #                         proc_conf["mipush_pkg_name"],
    #                         proc_conf["mipush_appsecret_ios"],
    #                         proc_conf["mipush_bundle_id"],
    #                         proc_conf["mipush_callback_url"]
    #                         )
    sms_sender = DayuSmsSender(appkey="23566149", secrt="f95d87510975317c9539d858c010f5a0")
    # Init web application
    webapp = Application(
        [
            (r"/msg/send_sms", send_sms.SendSMS),
            (r"/msg/send_verify_code", send_verify_code.SendVerify),
        ],
        autoreload=True,
        debug=True,
        sms_sender=sms_sender,
        )
    base_utils.try_listen_web(webapp, '0.0.0.0', options.port)
    ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
