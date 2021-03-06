# -*- coding: utf-8 -*-

import threading
import logging
import time
import traceback
import random
import copy

from tornado import ioloop, gen
from tornado.concurrent import Future

from concurrent.futures import ThreadPoolExecutor

import pymongo

logger = logging.getLogger()
class MongoDAOBaseException(Exception):
    def __init__(self, message, *args):
        self._msg = message % tuple(args)

    def __str__(self):
        return self._msg


class MongoMeta:
    def __init__(self, *args, **kwargs):
        # self.host = "119.23.51.192"
        self.host = "127.0.0.1"
        self.port = 27020
        self.username = 'longt'
        self.passwd = 'longt'
        self.repl_set_name = None
        self.max_thread_count = 3

        if "hosts" in kwargs:
            self.host = kwargs["hosts"]
        if "port" in kwargs:
            self.port = kwargs["port"]

        if "username" in kwargs:
            self.username = kwargs["username"]

        if "passwd" in kwargs:
            self.passwd = kwargs["passwd"]

        if "repl_set_name" in kwargs:
            self.repl_set_name = kwargs["repl_set_name"]

        if "max_thread_count" in kwargs:
            self.max_thread_count = kwargs["max_thread_count"]


class MongoDAOBase:
    def __init__(self, meta, **kwargs):
        self._meta = meta
        self._thread_pool = ThreadPoolExecutor(meta.max_thread_count)
        self._th_local = threading.local()

    def on_thread_init(self, th_local):
        pass

    def get_thread_local(self):
        return self._th_local

    def _inner_callback(self, **kwargs):
        __real_callback = kwargs["__real_callback"]

        if not hasattr(self._th_local, "mongo_client"):
            extra_args = {"w": 1, "j": True}

            '''
            logging.debug(
                "host:%s port:%d passwd:%s username:%s extra_args:%s",
                self._meta.host, self._meta.port, self._meta.passwd,
                self._meta.username, str(extra_args))
            '''
            mongo_client = pymongo.MongoClient(self._meta.host,
                                               self._meta.port, **extra_args)
            #print mongo_client
            mongo_client.get_database("admin").authenticate(
                self._meta.username,
                self._meta.passwd,
                mechanism='SCRAM-SHA-1')
            self._th_local.mongo_client = mongo_client
            self.on_thread_init(self._th_local)

            logger.debug("Init mongo success, host=%s port=%u replset=%s",
                         self._meta.host, self._meta.port,
                         self._meta.repl_set_name)
        kwargs["__mongo_client"] = self._th_local.mongo_client
        ret = __real_callback(self._th_local.mongo_client, **kwargs)
        return ret

    @gen.coroutine
    def submit(self, callback, **kwargs):
        kwargs["__real_callback"] = callback
        ret = yield self._thread_pool.submit(self._inner_callback, **kwargs)
        raise gen.Return(ret)

    def get_meta(self):
        return self._meta
