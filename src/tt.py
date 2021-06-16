# -*- coding: utf-8 -*-
# @Time     : 2021/6/16 16:42
# @Author   : Shigure_Hotaru
# @Email    : minjie96@sencyber.cn
# @File     : tt.py
# @Version  : Python 3.8.5 +

from sencyberApps.tools import SencyberLoggerReceiver


def run():
    slr = SencyberLoggerReceiver()
    slr.start()


if __name__ == '__main__':
    run()
    exit()
