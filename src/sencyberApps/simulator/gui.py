# -*- coding: utf-8 -*-
# @Time     : 2021/5/26 9:31
# @Author   : Shigure_Hotaru
# @Email    : minjie96@sencyber.cn
# @File     : gui.py
# @Version  : Python 3.8.5 +
import math
import time
import rawData

from dearpygui.core import *
from dearpygui.simple import *

from threading import Thread
from connection import Connection


class TestGui:
    def __init__(self, device_list: list, infos: dict):
        # Initialization
        self.device_list = device_list

        self.infos = infos

        self.__draw_windows()
        self.conn = None
        self.stt_time = 0
        self.stt_mode = 0

        self.flag = True

    def __get_current_time(self):
        now = time.time()
        now = math.floor(now)
        return now

    def start(self):

        start_dearpygui()

    def __get_logs(self):
        while self.flag:
            try:
                if self.conn is None:
                    continue
                elif len(self.conn.logs) != 0:
                    info = self.conn.read_logs()
                    log(info, logger="Info")
            except:
                continue

    def __draw_windows(self):
        set_main_window_size(1366, 768)
        set_exit_callback(self.__on_close)

        with window("Logger", width=600, height=700, x_pos=730, y_pos=20):
            add_logger("Info", log_level=0)

        with window("Function", width=700, height=700, x_pos=20, y_pos=20):
            add_same_line(spacing=10)
            add_text("Select The Device You Want To Simulate")

            # ===== Title =====
            add_spacing()
            add_same_line(spacing=10)
            add_listbox(items=self.device_list, width=300, num_items=4, name="Device")

            # ===== Online =====
            add_spacing(count=5)
            add_same_line(spacing=10)
            add_button("Connect", width=150, height=20, callback=self.__on_connect)
            add_same_line(spacing=10)
            add_text("Make Device Online")

            add_spacing()
            add_same_line(spacing=10)
            add_text("=" * 50)

            # ===== Start Trip =====
            add_spacing(count=5)
            add_same_line(spacing=10)
            add_button("Start_Trip", width=150, height=20, callback=self.__on_start_trip, enabled=False)
            add_same_line(spacing=10)
            add_text("Send Start Trip Data")

            add_spacing()
            add_same_line(spacing=10)
            add_input_text("stt_mode", default_value='0', height=30, width=50)
            add_same_line(spacing=10)
            add_input_text("stt_time", default_value='NOW', height=30, width=50)
            add_same_line(spacing=10)
            add_input_text("stt_gps_lat", default_value='31.4109', height=30, width=100)
            add_same_line(spacing=10)
            add_input_text("stt_gps_log", default_value='120.629575', height=30, width=100)

            add_spacing()
            add_same_line(spacing=10)
            add_input_text("stt_battery", default_value='90', height=30, width=50)
            add_same_line(spacing=10)
            add_input_text("stt_backup", default_value='70', height=30, width=50)
            add_same_line(spacing=10)
            add_input_text("stt_temperature", default_value='23.5', height=30, width=50)
            # ------------------
            add_spacing()
            add_same_line(spacing=10)
            add_text("-" * 50)
            # ------------------

            # ===== Send Angle =====
            add_spacing(count=3)
            add_same_line(spacing=10)
            add_button("Send_Angle", width=150, height=20, callback=self.__on_angle, enabled=False)
            add_same_line(spacing=10)
            add_text("Send Angle Data In Degree")
            add_same_line(spacing=10)
            add_input_text("Alpha", default_value='0.0', height=30, width=50)
            add_same_line(spacing=10)
            add_input_text("Beta", default_value='0.0', height=30, width=50)
            add_same_line(spacing=10)
            add_input_text("Theta", default_value='-90.0', height=30, width=50)
            # ------------------
            add_spacing()
            add_same_line(spacing=10)
            add_text("-" * 50)

            add_spacing(count=3)
            add_same_line(spacing=10)
            add_button("Send_Collision", width=150, height=20, callback=self.__on_collision, enabled=False)
            add_same_line(spacing=10)
            add_text("Send Harsh Event Data (Collision Only)")

            add_spacing()
            add_same_line(spacing=10)
            add_input_text("event_time", default_value='NOW', height=30, width=50)
            add_same_line(spacing=10)
            add_input_text("event_spd", default_value='50', height=30, width=50)

            add_spacing()
            add_same_line(spacing=10)
            add_input_text("event_gps_lat", default_value='31.4109', height=30, width=100)
            add_same_line(spacing=10)
            add_input_text("event_gps_log", default_value='120.629575', height=30, width=100)

            add_spacing()
            add_same_line(spacing=10)
            add_input_text(
                "event_data_path",
                default_value="2021-04-30-14-30-18-Collision-raw.csv",
                height=30, width=300
            )

            # ------------------
            add_spacing()
            add_same_line(spacing=10)
            add_text("-" * 50)
            # ------------------

            # ===== End Trip =====
            add_spacing(count=3)
            add_same_line(spacing=10)
            add_button("End_Trip", width=150, height=20, callback=self.__on_end_trip, enabled=False)
            add_same_line(spacing=10)
            add_text("Send End Trip Data")

            add_spacing()
            add_same_line(spacing=10)
            add_input_text("end_time", default_value='NOW', height=30, width=50)
            add_same_line(spacing=10)
            add_input_text("end_lat", default_value='31.361984', height=30, width=100)
            add_same_line(spacing=10)
            add_input_text("end_log", default_value='120.638813', height=30, width=100)

            add_spacing()
            add_same_line(spacing=10)
            add_input_text("end_battery", default_value='80', height=30, width=50)
            add_same_line(spacing=10)
            add_input_text("end_backup", default_value='70', height=30, width=50)
            add_same_line(spacing=10)
            add_input_text("end_temperature", default_value='25.5', height=30, width=50)

            add_spacing()
            add_same_line(spacing=10)
            add_input_text("end_score", default_value='100', height=30, width=50)
            add_same_line(spacing=10)
            add_input_text("end_harsh", default_value='[0, 0, 0, 0]', height=30, width=100)
            add_same_line(spacing=10)
            add_input_text("end_version", default_value='19', height=30, width=50)
            add_same_line(spacing=10)
            add_input_text("end_app", default_value='0', height=30, width=50)

            add_spacing()
            add_same_line(spacing=10)
            add_input_text("end_waiting_time", default_value='5', height=30, width=50)
            add_same_line(spacing=10)
            add_input_text("end_waiting_count", default_value='1', height=30, width=50)

            add_spacing()
            add_same_line(spacing=10)
            add_text("Harsh Event Order: Acc, Brake, Turn, Line Change")

            # ------------------
            add_spacing()
            add_same_line(spacing=10)
            add_text("-" * 50)
            # ------------------

            # ===== Re-Send-Info =====

            add_spacing()
            add_same_line(spacing=10)
            add_button("Re_Send_History", width=150, height=20, callback=self.__on_resend_history, enabled=False)
            add_same_line(spacing=10)
            add_button("Re_Send_Switch", width=150, height=20, callback=self.__on_resend_switch, enabled=False)
            add_same_line(spacing=10)
            add_button("Re_Send_Battery", width=150, height=20, callback=self.__on_resend_battery, enabled=False)

            # ------------------
            add_spacing(count=5)
            add_same_line(spacing=10)
            add_text("=" * 50)

            # ===== Offline =====
            add_spacing(count=1)
            add_same_line(spacing=10)
            add_button("Offline", width=150, height=20, callback=self.__on_close, enabled=False)
            add_same_line(spacing=10)
            add_text("Make Device Offline")
            #
            # add_button("Reconnect", width=100, height=30, callback=self.__on_reconnect)
            # add_same_line(spacing=10)
            # add_input_text("IP_ADDR", default_value='139.196.108.112', height=30, width=150)
            # add_spacing()
            # add_same_line(spacing=30)
            # add_text("When Disconnected, Press this button to reconnect")


            pass
        return

    def __on_resend_history(self, sender, data):
        data = [
            [1621473211, 1621484011, 0, 2, 0, 0],
            [1621484011, 1621494011, 0, 0, 0, 1],
            [1621494011, 1621499011, 1, 0, 0, 1],
        ]
        d = rawData.re_upload_history_trip(data)
        # print(tools.hex_to_str(d))
        self.conn.send(d, "Resend History")
        log_info("Resend Trip Info", logger="Info")
        return

    def __on_resend_switch(self, sender, data):
        data = [
            [1621473811, 0],
            [1621494311, 1]
        ]

        d = rawData.re_upload_switch(data)
        # print(tools.hex_to_str(d))
        self.conn.send(d, "Resend Switch")
        log_info("Resend Switch Info", logger="Info")
        return

    def __on_resend_battery(self, sender, data):
        data = [
            [1621473211, 0, 38, 88, 25.5],
            [1621476211, 1, 45, 70, 21.3]
        ]
        d = rawData.re_upload_battery(data)
        self.conn.send(d, "Resend Power")
        # print(tools.hex_to_str(d))
        log_info("Resend Power Info", logger="Info")
        return

    def __on_start_trip(self, sender, data):
        try:
            self.stt_mode = int(get_value("stt_mode"))
            stt_time = get_value("stt_time")

            if stt_time == "NOW":
                self.stt_time = self.__get_current_time()
            else:
                self.stt_time = int(stt_time)

            stt_gps_lat = float(get_value("stt_gps_lat"))
            stt_gps_log = float(get_value("stt_gps_log"))

            stt_battery = int(get_value("stt_battery"))
            stt_backup = int(get_value("stt_backup"))

            stt_temperature = float(get_value("stt_temperature"))
        except:
            log_error("Data Format Is Not Correct, Check Again.", logger="Info")
            return

        data = rawData.startCom(
            self.stt_mode,
            self.stt_time,
            stt_gps_log,
            stt_gps_lat,
            stt_battery,
            stt_backup,
            stt_temperature,
            b"\x99\x99\x99\x99\x99\x99"
        )

        self.conn.send(data, "Start Trip")
        configure_item("Start_Trip", enabled=False)
        time.sleep(1)
        log_debug("Trip Starts...", logger="Info")
        configure_item("Send_Angle", enabled=True)
        configure_item("Send_Collision", enabled=True)
        configure_item("End_Trip", enabled=True)

        return

    def __on_end_trip(self, sender, data):
        try:
            end_time = get_value("end_time")
            if end_time == "NOW":
                end_time = self.__get_current_time() + 60 * 3
            else:
                end_time = int(end_time)

            end_lat = float(get_value("end_lat"))
            end_log = float(get_value("end_log"))

            end_battery = int(get_value("end_battery"))
            end_backup = int(get_value("end_backup"))

            end_temperature = float(get_value("end_temperature"))
            end_score = int(get_value("end_score"))

            end_harsh = eval(get_value("end_harsh"))

            end_version = int(get_value("end_version"))
            end_app = int(get_value("end_app"))

            end_waiting_time = int(get_value("end_waiting_time"))
            end_waiting_count = int(get_value("end_waiting_count"))

            data = rawData.endCom(
                self.stt_mode,
                self.stt_time,
                end_time,
                end_log,
                end_lat,
                end_battery,
                end_backup,
                end_temperature,
                end_score,
                end_harsh,
                end_version,
                end_app,
                end_waiting_count,
                end_waiting_time
            )
        except:
            log_error("Data Format Is Not Correct, Check Again.", logger="Info")
            return
        configure_item("End_Trip", enabled=False)
        configure_item("Send_Angle", enabled=False)
        configure_item("Send_Collision", enabled=False)
        self.conn.send(data, "End Trips....")
        time.sleep(1)

        log_debug("Trip Ends...", logger="Info")

        configure_item("Start_Trip", enabled=True)
        return

    def __on_angle(self, sender, data):
        try:
            alpha = float(get_value("Alpha"))
            beta = float(get_value("Beta"))
            theta = float(get_value("Theta"))
        except:
            log_error("Data Format Is Not Correct, Check Again.", logger="Info")
            return

        d = rawData.angleInfo(alpha, beta, theta)
        self.conn.send(d, "Send Angle Info")
        return

    def __on_collision(self, sender, data):
        return

    def __on_connect(self, sender, data):
        self.flag = True

        thread = Thread(target=self.__get_logs)
        thread.start()

        device_id = get_value("Device")
        log_debug("Connecting to IOT...", logger="Info")
        log(f"Using Device Name: {self.device_list[device_id]}", logger="Info")
        configure_item("Device", enabled=False)
        configure_item("Connect", enabled=False)

        self.conn = Connection(self.infos[self.device_list[device_id]])
        if self.conn.connect():
            log("Success! Device Online.", logger="Info")
            configure_item("Offline", enabled=True)
            configure_item("Start_Trip", enabled=True)

            configure_item("Re_Send_History", enabled=True)
            configure_item("Re_Send_Battery", enabled=True)
            configure_item("Re_Send_Switch", enabled=True)

        else:
            log_error("Failed!", logger="Info")
            configure_item("Device", enabled=True)
            configure_item("Connect", enabled=True)
        return

    def __on_close(self, sender, data):
        log_debug("Disconnecting...", logger="Info")
        if self.conn is None:
            return
        configure_item("Offline", enabled=False)
        configure_item("Start_Trip", enabled=False)
        configure_item("Send_Angle", enabled=False)
        configure_item("Send_Collision", enabled=False)
        configure_item("End_Trip", enabled=False)

        if self.conn.disconnect():
            configure_item("Device", enabled=True)
            configure_item("Connect", enabled=True)
            log("Device Offline", logger="Info")

            configure_item("Re_Send_History", enabled=False)
            configure_item("Re_Send_Battery", enabled=False)
            configure_item("Re_Send_Switch", enabled=False)

        else:
            log_error("Offline Failed", logger="Info")
            configure_item("Offline", enabled=True)
        self.flag = False

        self.conn = None
        return
