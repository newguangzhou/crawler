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
from db.auth.auth_dao import AuthDAO
from db.user.user_dao import UserDAO
from db.mongo_dao_base import MongoMeta

from rpc.msg_rpc import MsgRPC

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
        auth_dao=AuthDAO.new(mongo_meta=MongoMeta()),
        user_dao=UserDAO.new(mongo_meta=MongoMeta()),
    )
    webapp.settings["msg_rpc"] = MsgRPC("http://127.0.0.1:9200")


    base_utils.try_listen_web(webapp, '0.0.0.0', options.port)

    ioloop.IOLoop.current().start()


