# -*- coding: utf-8 -*-
# @Time     : 2021/6/15 11:28
# @Author   : Shigure_Hotaru
# @Email    : minjie96@sencyber.cn
# @File     : try.py
# @Version  : Python 3.8.5 +

import logging
import time

from sencyberApps.tools import SencyberLogger

sl = SencyberLogger(receiver_address="127.0.0.1")
logging.info("Try 1 Try")
logging.info("Try 2 Try")
logging.info("Try 3 Try")

time.sleep(2)
sl.end()
