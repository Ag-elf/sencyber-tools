# -*- coding: utf-8 -*-
# @Time     : 2021/3/22 13:20
# @Author   : Shigure_Hotaru
# @Email    : minjie96@sencyber.cn
# @File     : tools.py
# @Version  : Python 3.8.5 +

import math
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable


class PositionAHRS:
    def __init__(self):
        self.beta = 0
        self.pi = 0
        self.q = [1.0, 0.0, 0.0, 0.0]

    def update(self, acc, w, SamplePeriod=1 / 20, Beta=0.1):
        """
        This function is used to update the quaternion
        :param acc:             (x, y, z)       :acceleration
        :param w:               (wx, wy, wz)    :gyroscope readings
        :param SamplePeriod:    1/20 by default :hz
        :param Beta:            0.1 by default  :hyper parameter
        :return:
        """
        ax, ay, az = acc
        gx, gy, gz = w
        gx = gx / 180 * math.pi
        gy = gy / 180 * math.pi
        gz = gz / 180 * math.pi
        q1 = self.q[0]
        q2 = self.q[1]
        q3 = self.q[2]
        q4 = self.q[3]

        _2q1 = 2 * q1
        _2q2 = 2 * q2
        _2q3 = 2 * q3
        _2q4 = 2 * q4
        _4q1 = 4 * q1
        _4q2 = 4 * q2
        _4q3 = 4 * q3
        _8q2 = 8 * q2
        _8q3 = 8 * q3
        q1q1 = q1 * q1
        q2q2 = q2 * q2
        q3q3 = q3 * q3
        q4q4 = q4 * q4

        norm = math.sqrt(ax * ax + ay * ay + az * az)
        if norm == 0.0:
            return
        norm = 1 / norm
        ax *= norm
        ay *= norm
        az *= norm

        s1 = _4q1 * q3q3 + _2q3 * ax + _4q1 * q2q2 - _2q2 * ay
        s2 = _4q2 * q4q4 - _2q4 * ax + 4 * q1q1 * q2 - _2q1 * ay - _4q2 + _8q2 * q2q2 + _8q2 * q3q3 + _4q2 * az
        s3 = 4 * q1q1 * q3 + _2q1 * ax + _4q3 * q4q4 - _2q4 * ay - _4q3 + _8q3 * q2q2 + _8q3 * q3q3 + _4q3 * az
        s4 = 4 * q2q2 * q4 - _2q2 * ax + 4 * q3q3 * q4 - _2q3 * ay

        norm = 1 / math.sqrt(s1 * s1 + s2 * s2 + s3 * s3 + s4 * s4)
        s1 *= norm
        s2 *= norm
        s3 *= norm
        s4 *= norm

        qDot1 = 0.5 * (-q2 * gx - q3 * gy - q4 * gz) - Beta * s1
        qDot2 = 0.5 * (q1 * gx + q3 * gz - q4 * gy) - Beta * s2
        qDot3 = 0.5 * (q1 * gy - q2 * gz + q4 * gx) - Beta * s3
        qDot4 = 0.5 * (q1 * gz + q2 * gy - q3 * gx) - Beta * s4

        q1 += qDot1 * SamplePeriod
        q2 += qDot2 * SamplePeriod
        q3 += qDot3 * SamplePeriod
        q4 += qDot4 * SamplePeriod

        norm = 1 / math.sqrt(q1 * q1 + q2 * q2 + q3 * q3 + q4 * q4)

        self.q[0] = q1 * norm
        self.q[1] = q2 * norm
        self.q[2] = q3 * norm
        self.q[3] = q4 * norm
        return

    def get_euler(self):
        """
        From quaternion to euler angles roll, pitch, yaw
        :return: alpha, beta, theta in rad
        """
        alpha = math.atan2(2 * (self.q[0] * self.q[1] + self.q[2] * self.q[3]),
                           1 - 2 * (self.q[1] * self.q[1] + self.q[2] * self.q[2]))
        beta = math.asin(2 * (self.q[0] * self.q[2] - self.q[3] * self.q[1]))
        theta = math.atan2(2 * (self.q[0] * self.q[3] + self.q[1] * self.q[2]),
                           1 - 2 * (self.q[2] * self.q[2] + self.q[3] * self.q[3]))

        return alpha, beta, theta


class ConcurrentHandler:
    def __init__(self, max_workers: int, call_back: Callable):
        self.__threadPool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="sencyber")
        self.__call_back = call_back

        self.__future_list = []

    def submit(self, *args):
        f = self.__threadPool.submit(self.__call_back, *args)
        self.__future_list.append(f)

    def isDone(self):
        for f in self.__future_list:
            if not f.done():
                return False

        return True

    def getResult(self):
        while not self.isDone():
            time.sleep(5)
            continue

        result = []
        for f in self.__future_list:
            result.append(f.result())
        return result


def a_to_hex(val: int) -> str:
    if val < 10:
        return str(val)
    elif val == 10:
        return 'A'
    elif val == 11:
        return 'B'
    elif val == 12:
        return 'C'
    elif val == 13:
        return 'D'
    elif val == 14:
        return 'E'
    elif val == 15:
        return 'F'


def hex_to_str(payload: bytes) -> str:
    raw = ""
    for d in payload:
        ten = a_to_hex(d // 16)
        one = a_to_hex(d % 16)
        raw = raw + ten + one + " "

    return raw


