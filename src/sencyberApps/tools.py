# -*- coding: utf-8 -*-
# @Time     : 2021/3/22 13:20
# @Author   : Shigure_Hotaru
# @Email    : minjie96@sencyber.cn
# @File     : tools.py
# @Version  : Python 3.8.5 +
import json
import math
import os
import socket
import logging
import struct
import time
import traceback

from concurrent.futures import ThreadPoolExecutor

from queue import Queue
from threading import Lock, Thread
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


# Auto Queue, Get if Full
class AutoQueue:
    # Initializing
    def __init__(self, length: int):
        self.queue = Queue()
        self.length = length

    def __str__(self):
        raw = ""
        for item in self.queue.queue:
            raw += "&,&"
            raw += item
        return raw

    def put(self, item):
        """
        This function is called when you want to put an item into the queue
        :param item: item, can be anything you want
        :return:
        """
        self.queue.put(item)
        if self.queue.qsize() > self.length:
            self.queue.get()

    def get(self):
        """
        This function is used to get the item in the queue. (Item consumed when calling the function)
        :return:
        """
        item = self.queue.get()
        return item

    def clean(self):
        """
        Clean the queue
        :return:
        """
        self.queue.queue.clear()

    def getQueue(self):
        """
        Get the actual list of items for the queue.
        :return:
        """
        return self.queue.queue

    def isFull(self):
        return self.queue.full()


class SencyberLogger:
    def __init__(self, receiver_address='0.0.0.0', receiver_port=10080, title='default', auto_interval=1200):
        self.receiver_address = receiver_address
        self.receiver_port = receiver_port
        self.title = title
        self.time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        self.auto_interval = auto_interval

        self.file_name = f'{self.time}_{title}'
        self.__running = 1
        self.__lock = Lock()

        LOG_FORMAT = "%(asctime)s [%(levelname)s]: %(message)s @ [%(module)s-%(lineno)s]"
        logging.basicConfig(
            filename=f"{self.file_name}.log",
            level=logging.DEBUG,
            format=LOG_FORMAT,
        )

        logging.FileHandler(filename=f"{self.file_name}.log", encoding="utf-8")

        self.__thread = Thread(target=self.__backUp)
        self.__thread.start()
        logging.info(f"{self.title} Logger Initialization Complete.")

    def sendLogging(self):
        logging.debug(f"Prepare to send logs...")
        if self.receiver_address == "0.0.0.0":
            logging.warning(f"Server address is not specified, logs will not be uploaded.")
            return
        for i in range(5):
            logging.debug(f"Try to upload logs to server {self.receiver_address}:{self.receiver_port}")
            state = self.__send_logs()
            if state == 0:
                break

    def __send_logs(self):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.receiver_address, self.receiver_port))

            client.settimeout(10)
            client.send(b"\x55\xAASTT\xED")
            dat = client.recv(10)
            if dat == b"\x55\xAARCV\xED":
                file_path = f"{self.file_name}.log"
                if not os.path.exists(file_path):
                    logging.error(f"{file_path} Not Exist")
                    return 1
                with open(file_path, 'r') as f:
                    data = f.read().encode(encoding="utf-8")
                    # print(date)
                    size = len(data)

                header = {
                    'file_name': self.title,
                    'length': size,
                    'stt_time': self.time
                }
                header_json = json.dumps(header)
                header_bytes = header_json.encode('utf-8')

                s_header = struct.pack('i', len(header_bytes))

                client.send(s_header)
                client.send(header_bytes)
                client.send(data)
            else:
                logging.error(f"{self.receiver_address}:{self.receiver_port} is not a proper log server.")
                return 1
        except ConnectionResetError:
            logging.error(f"Connection Reset By Peer.")
            return 1
        except TimeoutError:
            logging.error(f"Connection Time Out.")
            return 1
        except Exception:
            logging.error(f"Unhandled Exception Occurred: {traceback.format_exc()}")
            return 1
        return 0

    def __backUp(self):
        counter = 0
        while self.__running == 1:
            time.sleep(1)
            counter += 1
            if counter == self.auto_interval:
                self.__lock.acquire()
                logging.debug(f"Backup logs...")
                self.sendLogging()
                self.__lock.release()
                counter = 0

    def end(self):
        logging.info("End Logging...")
        self.__running = 0
        self.__lock.acquire()
        self.sendLogging()
        self.__lock.release()


class SencyberLoggerReceiver:
    def __init__(self, bind_address="0.0.0.0", bind_port=10080, path="./"):
        LOG_FORMAT = "%(asctime)s [%(levelname)s]: %(message)s @ [%(module)s-%(lineno)s]"
        logging.basicConfig(
            level=logging.DEBUG,
            format=LOG_FORMAT
        )
        self.__path = path
        self.__bind_address = bind_address
        self.__bind_port = bind_port
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind((self.__bind_address, self.__bind_port))
        self.__server.listen(50)
        self.__threadPool = ThreadPoolExecutor(max_workers=50, thread_name_prefix="sencyber")
        self.__lock = Lock()
        logging.info("Sencyber Logger Receiver Start")

    def start(self):
        while True:
            conn, address = self.__server.accept()
            self.__threadPool.submit(self.__handle, conn=conn, address=address)

    def __handle(self, conn: socket, address):
        try:
            data = conn.recv(6)
            if data == b"\x55\xAASTT\xED":
                self.__lock.acquire()
                self.__lock.release()
                conn.send(b"\x55\xAARCV\xED")

                s_header = conn.recv(4)
                s_header = struct.unpack('i', s_header)[0]

                b_header = conn.recv(s_header)

                json_header = b_header.decode('utf-8')
                header = json.loads(json_header)

                file_size = header['length']
                stt_time = header['stt_time']
                file_name = f"{stt_time}_{header['file_name']}_RCV.log"

                logging.info(f"{file_name} Saving Incoming Logs...")

                res = b""
                size = 0
                while size < file_size:
                    data = conn.recv(2048)
                    size += len(data)
                    res += data

                with open(self.__path + file_name, 'w+') as f:
                    res = res.replace(b"\r\n", b"\n")
                    # print(res[500:590])
                    # print(res)
                    pp = res.decode(encoding="utf-8", errors="ignore").strip()
                    # print(pp)
                    f.write(pp)

                logging.info(f"{file_name} Saved Successfully!!")

        except Exception:
            logging.error("=" * 50)
            logging.error("Exception!!")
            logging.error(traceback.format_exc())
            logging.error("=" * 50)

        conn.close()
        return


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


