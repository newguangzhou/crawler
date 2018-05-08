# -*- coding: utf-8 -*-

import setproctitle
import logging, os
from tornado import gen
import tornado.options

from tornado.ioloop import IOLoop

# from lib.sys_config import SysConfig
from configs.constants import *

import time
import socket






"""
   初始化服务,包括:
   注册服务
   设置日志
"""
def init_service(service_name, log_level=logging.INFO):
    # 设置进程名称
    setproctitle.setproctitle(service_name)
    # 读取配置文件
    # conf = loadJsonConfig()
    # app_conf = conf[service_name]
    # mongo_conf = MongoConfig2(conf["mongodb"])
    #debug = conf.get("debug_mode", False)
    # 分析tornado 命令行参数
    # !!!!! 注意!!!! parse_command_line()会更改日志配置，所以这条指令必须在set_logger()前执行
    tornado.options.parse_command_line()
    # 优先从配置文件获取服务监听IP,如果没有配置，则获取本地IP
    # if "ip" in app_conf:
    #     ip = app_conf["ip"]
    # else:
    #     ip = get_local_ip()
    # 获取配置端口
    # port = app_conf["port"]
    # 设置日志
    set_logger(service_name, log_level)
    # 全局定时器
    # sched = create_sched(conf['mongodb'], service_name)
    # sched.start()
    # 打开sysconfig
    # SysConfig.new(mongo_meta=mongo_conf.global_mongo_meta)
    Constants.new()
    # IOLoop.current().run_sync(SysConfig.current().open)
    # res = {
    #     "conf":conf,
    #     "proc_conf":conf[service_name],
    #     "mongo_conf":mongo_conf,
    #     "sched":sched,
    #     "ip":ip,
    #     "port":port
    # }
    # return res

def set_logger(proc_name, log_level):
    logger = logging.getLogger()
    logger.setLevel(log_level)
    # 使用设备LOG_LOCAL0
    # /dev/log是一个unix socket
    # sys_handler = logging.handlers.SysLogHandler('/dev/log', facility=logging.handlers.SysLogHandler.LOG_LOCAL0)
    # sys_handler.setFormatter(logging.Formatter(
    #     fmt=proc_name + " %(asctime)s,%(msecs)d [%(levelname)s] [%(filename)s:%(lineno)d] <%(process)d> %(message)s",
    #     datefmt="%a %m-%d %H:%M:%S"))
    # logger.handlers=[sys_handler]
    filehandler = logging.FileHandler(os.environ['HOME'] + '/Server.log', encoding='utf8')
    filehandler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(filehandler)
    return logger



"""
尝试监听指定的端口，被占用的情况下，自动+1
返回实际监听的端口
"""
def try_listen_web(obj, ip, port):
    while(True):
        try:
            obj.listen(port,ip, xheaders=True)
        except Exception as e:
            logging.warning("listen at %s:%d fail. try next port. error:%s", ip, port, e)
            port += 1
            time.sleep(1)
            continue
        return port


def get_local_ip():
    #获取本机电脑名
    myname = socket.getfqdn(socket.gethostname(  ))
    #获取本机ip
    myaddr = socket.gethostbyname(myname)
    return myaddr

import requests


def date2int(dt):
    return int(time.mktime(dt.timetuple()))




