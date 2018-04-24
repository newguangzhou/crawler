# -*- coding: utf-8 -*-
from zlib import crc32
import time

import datetime


import logging
logger = logging.getLogger(__name__)


import re



def gen_gid():
    return crc32(bytes(str(time.time()), encoding='utf-8'))



def date2str(dt, no_time=False):
    if isinstance(dt, datetime.datetime):
        if no_time:
            return "%02u-%02u-%02u" % (dt.year, dt.month, dt.day)
        else:
            return "%02u-%02u-%02u %02u:%02u:%02u" % (
                dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    elif isinstance(dt, datetime.date):
        return "%02u-%02u-%02u" % (dt.year, dt.month, dt.day)
    else:
        return ""



def recover_log(title, **kwargs):
    msg = "[recover] title=\"%s\"," % (title,)
    i = 0
    for (k, v) in list(kwargs.items()):
        if isinstance(v, int) or isinstance(v, float):
            msg += "%s=%s" % (k, str(v))
        elif isinstance(v, str):
            msg += "%s=\"%s\"" % (k, v)
        else:
            msg += "%s=\"%s\"" % (k, str(v))
        if i != len(kwargs) - 1:
            msg += ","
        i += 1
    logger.error(msg)


def is_imei_valide(imei):
    if imei is None or len(imei) != 15 or imei.find('35739608') != 0:
        return False
    check_list = []
    index = 0
    e_sum = 0
    i_sum = 0
    for item in imei:
        value = int(item)
        if index < 14:
            if index % 2 == 0:
                e_sum += value
            else:
                i_sum += (int(value * 2 / 10) + (value * 2 % 10))
        check_list.append(value)
        index += 1
    imei15 = (10 - ((e_sum + i_sum) % 10)) % 10
    if imei15 == check_list[14]:
        return True
    else:
        return False




def is_valid_phone_num(phone_num):
    p = re.compile(
        '^((13[0-9])|(14[0-9])|(15[0-9])|(16[0-9])|(17[0-9])|(18[0-9])|(19[0-9]))\d{8}$')
    return p.match(phone_num)