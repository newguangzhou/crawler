import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.web import Application

import sys
import importlib
sys.path.append("../../")
importlib.reload(sys)

import logging
import handlers
from utils import base_utils

from tornado.options import define,options
from tornado import ioloop

define("port",default=443,help="run tornado service",type=int)


proctitle = "user_srv_d"

if __name__=="__main__":
    base_utils.init_service(proctitle, logging.DEBUG)
    webapp=Application(
        [(r"/user/get_verify_code", handlers.GetVerifyCode),
        (r"/user/login", handlers.Login),
        (r"/user/logout", handlers.Logout),
         (r"/test",handlers.TestHandler)
         ],
        autoreload=True,
        debug=True,
    )
    base_utils.try_listen_web(webapp, '0.0.0.0', options.port)

    ioloop.IOLoop.current().start()


