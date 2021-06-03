# -*- coding: utf-8 -*-
# @Time     : 2021/4/6 10:39
# @Author   : Shigure_Hotaru
# @Email    : minjie96@sencyber.cn
# @File     : rawData.py
# @Version  : Python 3.8.5 +
import pandas as pd


def __parseFixNumber(value: float, precise: int, sizeInt: int, sizePoint: int) -> bytes:
    try:
        data = b''
        val = str(value).split('.')
        data += int(val[0]).to_bytes(sizeInt, byteorder='big')
        if len(val) == 1:
            val.append('0')
        while len(val[1]) < precise:
            val[1] += '0'

        if len(val[1]) > precise:
            val[1] = val[1][:8]

        data += int(val[1]).to_bytes(sizePoint, byteorder='big')
    except OverflowError as e:
        data = b'__parseFixNumber: Data is too large'

    return data


def __parseGpsData(log, lat, spd=-1.0):
    data = b''
    # Lat
    # \x45 --->>> E
    data += b'\x45'
    data += __parseFixNumber(log, 8, 1, 4)

    # Log
    # \x4E --->>> N
    data += b'\x4E'
    data += __parseFixNumber(lat, 8, 1, 4)

    if spd <= 0:
        return data
    data += __parseFixNumber(spd, 2, 2, 1)
    return data


def __parseIMUData(acc, w, flag=0):
    data = b''
    if flag == 0:
        temp = 0x8000
        for ac in acc:
            if ac < 0:
                ac = abs(ac)
                if ac > 32768:
                    ac = 0x7FFF
                ac = ac | temp
            data += ac.to_bytes(2, byteorder='big')

        for ac in w:
            if ac < 0:
                ac = abs(ac)
                if ac > 32768:
                    ac = 0x7FFF
                ac = ac | temp
            data += ac.to_bytes(2, byteorder='big')
        return data
    elif flag == 1:
        for ac in acc:
            data += ac
        for gy in w:
            data += gy
        return data


def __parseTemperature(temperature):
    data = b''
    if temperature < 0:
        data += b'\x02'
    elif temperature > 0:
        data += b'\x01'
    else:
        data += b'\x00'
    data += __parseFixNumber(abs(temperature), 2, 1, 1)
    return data


# Real Time GPS Data
def realTimeGPS(trip_stt, data_stt, sampleTime=3000, gps=None):
    data = b'\x03'
    if gps is None:
        gps = [(114.24071183, 30.00043864, 18.34), (86.24071183, 30.0109244, 50.21)]

    data += trip_stt.to_bytes(4, byteorder='big')
    data += data_stt.to_bytes(4, byteorder='big')

    data += sampleTime.to_bytes(2, byteorder='big')
    data += len(gps).to_bytes(1, byteorder='big')

    for raw in gps:
        log, lat, spd = raw
        data += __parseGpsData(log, lat, spd)

    return data


# Start and End Data
def startData(mode, timestamp_stt, log, lat, battery, backup_battery, temperature, mac_add=b'', timestamp_end=0, score=100):
    data = b''

    if mode == 1:
        data += b'\x01'
    else:
        data += b'\x02'

    # Time Stamp
    data += timestamp_stt.to_bytes(4, byteorder='big')

    if mode != 1:
        data += timestamp_end.to_bytes(4, byteorder='big')

    data += b'\x45'
    data += __parseFixNumber(log, 8, 1, 4)

    data += b'\x4E'
    data += __parseFixNumber(lat, 8, 1, 4)

    data += battery.to_bytes(1, byteorder='big')
    data += backup_battery.to_bytes(1, byteorder='big')

    data += __parseTemperature(temperature)
    if mode == 1:
        while len(mac_add) < 6:
            mac_add += b'\x99'

        data += mac_add
    else:
        data += score.to_bytes(1, byteorder='big')
    return data


# Start Communication
def startCom(mode, timestamp_stt, log, lat, battery, backup_battery, temperature, mac_add):
    data = b'\x81'
    data += mode.to_bytes(1, byteorder='big')
    data += timestamp_stt.to_bytes(4, byteorder='big')

    data += b'\x45'
    data += __parseFixNumber(log, 8, 1, 4)

    data += b'\x4E'
    data += __parseFixNumber(lat, 8, 1, 4)

    data += battery.to_bytes(1, byteorder='big')
    data += backup_battery.to_bytes(1, byteorder='big')

    data += __parseTemperature(temperature)
    while len(mac_add) < 6:
        mac_add += b'\x99'
    data += mac_add

    return data


# End Communication
def endCom(mode, stt, end, log, lat, battery, backup_battery, temperature, score, harsh, version, app, waiting_count, waiting_time):
    data = b'\x82'
    data += mode.to_bytes(1, byteorder='big')
    data += stt.to_bytes(4, byteorder='big')
    data += end.to_bytes(4, byteorder='big')

    if log == -999:
        data += b'\xFF\xFF\xFF\xFF\xFF\xFF'
    else:
        data += b'\x45'
        data += __parseFixNumber(log, 8, 1, 4)

    if lat == -999:
        data += b'\xFF\xFF\xFF\xFF\xFF\xFF'
    else:
        data += b'\x4E'
        data += __parseFixNumber(lat, 8, 1, 4)

    data += battery.to_bytes(1, byteorder='big')
    data += backup_battery.to_bytes(1, byteorder='big')

    data += __parseTemperature(temperature)

    data += score.to_bytes(1, byteorder='big')
    harsh_val = harsh[0]
    for d in range(len(harsh) - 1):
        harsh_val = harsh_val << 8
        harsh_val += harsh[d + 1]
    data += harsh_val.to_bytes(4, byteorder='big')
    data += version.to_bytes(4, byteorder='big')

    if app == 0:
        data += b'\x00'
    else:
        data += b'\x01'

    if waiting_count == -1 or waiting_time == -1:
        return data
    data += waiting_count.to_bytes(2, byteorder='big')
    data += waiting_time.to_bytes(4, byteorder='big')

    return data


# IMU data
def IMUData(mode, trip_stt, event_stt, before=10, after=5, imu_raw=None):
    if imu_raw is None:
        imu_list = [[(1, 1, 1), (1, 1, 1)]] * 320
        flag = 0
    else:
        imu_list = []
        data = pd.read_csv(imu_raw)
        raw_data = data.values
        for line in raw_data:
            imu_list.append([(eval(line[1]), eval(line[2]), eval(line[3])), (eval(line[4]), eval(line[5]), eval(line[6]))])
        flag = 1
    head = b'\x04' + mode.to_bytes(1, byteorder='big')
    head += trip_stt.to_bytes(4, byteorder='big')

    event_stt *= 1000
    head += event_stt.to_bytes(6, byteorder='big')

    head += before.to_bytes(1, byteorder='big')
    head += after.to_bytes(1, byteorder='big')

    head += b'\x10'

    imu_d = b''
    data_list = []
    for i in range(len(imu_list)):
        imu_data = imu_list[i]
        pkg = i // 20 + 1
        imu_d += __parseIMUData(imu_data[0], imu_data[1], flag)
        if len(imu_d) == 12 * 20:
            data_list.append(head + pkg.to_bytes(1, byteorder='big') + imu_d)
            imu_d = b''

    return data_list


# Harsh Event Data
def harshEvent(mode, trip_stt, event_stt, log, lat, spd):
    head = b'\x06' + mode.to_bytes(1, byteorder='big')
    head += trip_stt.to_bytes(4, byteorder='big')

    event_stt *= 1000
    head += event_stt.to_bytes(6, byteorder='big')

    head += __parseGpsData(log, lat, spd)
    return head


# Device Angle Data
def angleInfo(alpha: float, beta: float, theta: float) -> bytes:
    data = b'\x08'
    w = (theta, alpha, beta)
    for angle in w:
        if angle < 0:
            data += b'\x01'
        else:
            data += b'\x00'
        data += __parseFixNumber(abs(angle), 2, 1, 1)

    return data


# Switch Open
# ToDo Fix The Algo
def switch(time: int, log: float, lat: float, battery: int, backup_battery: int, temperature: float, state: int) -> bytes:
    data = b'\x07'
    data += time.to_bytes(4, byteorder='big')
    data += __parseGpsData(log, lat)
    data += __parseTemperature(temperature)
    if state == 0:
        data += b'\x00'
    else:
        data += b'\x01'
    return data


# GPS Check
def gps_check(log: float, lat: float, spd: float):
    data = b"\x83"
    data += __parseGpsData(log, lat, spd)
    return data


# start, end, harsh event x 4
def re_upload_history_trip(trips: list):
    data = b'\x09'
    data += len(trips).to_bytes(1, byteorder='big')

    for trip in trips:
        data += trip[0].to_bytes(4, byteorder='big')
        data += trip[1].to_bytes(4, byteorder='big')

        data += trip[2].to_bytes(1, byteorder='big')
        data += trip[3].to_bytes(1, byteorder='big')
        data += trip[4].to_bytes(1, byteorder='big')
        data += trip[5].to_bytes(1, byteorder='big')

    return data


# time, state
def re_upload_switch(times: list):
    data = b'\x0a'
    data += len(times).to_bytes(1, byteorder='big')

    for trip in times:
        data += trip[0].to_bytes(4, byteorder='big')
        data += trip[1].to_bytes(1, byteorder='big')

    return data


# time, state, power, back, temp
def re_upload_battery(power: list):
    data = b'\x0b'
    data += len(power).to_bytes(1, byteorder='big')
    for trip in power:
        data += trip[0].to_bytes(4, byteorder='big')
        data += trip[1].to_bytes(1, byteorder='big')

        data += trip[2].to_bytes(1, byteorder='big')
        data += trip[3].to_bytes(1, byteorder='big')

        data += __parseTemperature(trip[4])

    return data


if __name__ == '__main__':

    # d = gps_check(86.24071183, 30.0109244, 50.21)
    # print(d)
    d2 = b'\x83' + b'\xFF' * 15
    print(d2)
    # raw = "../../data/IMU_data/2021-04-25-14-34-10-Collision-raw.csv"
    # k = IMUData(0, 0, 0, before=10, after=5, imu_raw=raw)
    # print(len(k))
