# -*- coding: utf-8 -*-

from .helper_handler import HelperHandler
from tornado import gen
import logging


class TestHandler(HelperHandler):
    @gen.coroutine
    def _deal_request(self):
        logging.debug("OnLogin, %s", self.dump_req())
        res={"test":"test"}
        return res

