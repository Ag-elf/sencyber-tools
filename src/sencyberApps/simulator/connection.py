# -*- coding: utf-8 -*-
# @Time     : 2021/4/6 14:30
# @Author   : Shigure_Hotaru
# @Email    : minjie96@sencyber.cn
# @File     : connection.py
# @Version  : Python 3.8.5 +

from linkkit import linkkit
import time
import sencyberApps.tools as tools
import rawData
from threading import Lock


def on_connect(session_flag, rc, userdata):
    print("Connecting...")
    pass


def on_disconnect(rc, userdata):
    print("Disconnecting...")
    pass


def on_topic_message(topic, payload, qos, userdata):
    global flag
    # print("on_topic_message:" + topic + " payload:" + str(payload) + " qos:" + str(qos))
    flag = False
    pass


def on_unsubscribe_topic(mid, userdata):
    print("on_unsubscribe_topic mid:%d" % mid)
    pass


def on_subscribe_topic(mid, granted_qos, userdata):
    print("on_subscribe_topic mid:%d, granted_qos:%s" %
          (mid, str(','.join('%s' % it for it in granted_qos))))
    pass


# def on_thing_raw_data_arrived(payload, userdata):
#     print("on_thing_raw_data_arrived:%s" % str(payload))
#     if payload == b'\x83':
#         d = rawData.gps_check(120.601186, 31.31858, )

class Connection:
    def __init__(self, inf):

        infos = inf

        # Aliyun IOT 的接口
        self.lk = linkkit.LinkKit(
            host_name=infos['hostName'],
            product_key=infos['iotProductKey'],
            device_name=infos['iotDeviceName'],
            device_secret=infos['iotDeviceSecret'])

        self.lk.on_connect = on_connect
        self.lk.on_disconnect = on_disconnect
        self.lk.on_topic_message = on_topic_message
        self.lk.on_subscribe_topic = on_subscribe_topic
        self.lk.on_unsubscribe_topic = on_unsubscribe_topic
        self.lk.on_thing_raw_data_arrived = self.on_thing_raw_data_arrived
        self.lk.config_mqtt(secure="", endpoint=infos['endPoint'], max_queued_message=10)

        self.GPS_data_counter = 0
        self.GPS_data = [
            rawData.gps_check(120.601186, 31.31858, 50.21),
            rawData.gps_check(120.602186, 31.31858, 50.21),
            rawData.gps_check(120.603186, 31.31858, 50.21),
            rawData.gps_check(120.604186, 31.31858, 50.21),
            rawData.gps_check(120.605186, 31.31858, 50.21),
            rawData.gps_check(120.606186, 31.31858, 50.21),
            rawData.gps_check(120.607186, 31.31858, 50.21),
        ]
        self.lock = Lock()
        self.logs = []

    def send(self, data, info='Default'):
        print(f"Send Data: {info}")
        self.lk.thing_raw_post_data(data)
        self.lock.acquire()
        self.logs.append(info)
        self.logs.append(f"Raw: {tools.hex_to_str(data)}")
        self.lock.release()

    def connect(self):
        try:
            self.lk.connect_async()
            self.lk.start_worker_loop()
            time.sleep(1)
            return True
        except:
            return False

    def disconnect(self):
        try:
            self.lk.disconnect()
            time.sleep(1)
            return True
        except:
            return False

    def set_gps_data(self, data: list):
        self.GPS_data = data

    def on_thing_raw_data_arrived(self, payload, userdata):
        print("=== on_thing_raw_data_arrived:%s ===" % str(payload))
        self.lock.acquire()
        self.logs.append(f"Receive Raw: {tools.hex_to_str(payload)}")
        self.lock.release()
        if payload[0] == 0x81:
            info = "Reply Info: Start Trip, "
            miles = int.from_bytes(payload[1:5], byteorder="big")
            info += f"Total Mileage: {miles}"

            if len(payload) >= 6:
                if payload[5] == 0x01:
                    info += ", Turn on GPS trace"

            self.lock.acquire()
            self.logs.append(info)
            self.lock.release()

            print(info)

        elif payload[0] == 0x82:
            info = "Reply Info: End Trip, "
            if payload[2] == 0x01:
                info += "Needs Update"
            else:
                info += "No Update"

            self.lock.acquire()
            self.logs.append(info)
            self.lock.release()
            print(info)

        elif payload == b'\x83':
            # Make sure that the terminal can receive the message
            self.GPS_data_counter %= len(self.GPS_data)
            d = self.GPS_data[self.GPS_data_counter]

            self.send(d, "GPS Check Requested")
            time.sleep(1)
            print("GPS Data Sent")
            self.GPS_data_counter += 1

            self.lock.acquire()
            # self.logs.append("GPS Check Requested...")
            self.logs.append(f"Data Sent: {tools.hex_to_str(d)}")
            self.lock.release()

    def read_logs(self):
        self.lock.acquire()
        try:
            info = self.logs.pop(0)
        except:
            info = "N/A"
        self.lock.release()
        return info
