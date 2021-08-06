import time
import pymysql
from datetime import datetime
from .db_operations import *
from .control_functons import *
import numpy as np

def taskFunction(self, id, adjDirection, datalist):
    if id[:4] == "pump":
        # db connection
        db = pymysql.connect(host="localhost", user="root", passwd="cfins", db="data", charset='utf8')
        cursor = db.cursor()

        cur_date = datetime.now().strftime("%Y%m%d")
        zero_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 0, 0)
        clear_con_db(db, 2)
        step = 0
        
        vfd_frequency_con = 40.0
        step_length = 20            # transport to hp node or sync to hp node
        step_count = 0

        # 阻塞性地获取水泵path
        data, path, __ = self.descendantData.get()
        
        while True:
            start_time = datetime.now()
            db_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
            try:
                # 定时开关机
                cur_weekday = start_time.strftime("%A")        # 当前星期
                cur_date = datetime.now().strftime("%Y%m%d")
                auto_open_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 7, 50)       # 自动开机时间 
                auto_close_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 18, 10)     # 自动关机时间

                if cur_weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:      # 工作日
                    if datetime.now() > auto_open_time and datetime.now() <= auto_close_time:    # 启停时间内
                        # Read states
                        outdoor_temp_list = []
                        p_sup_list = []
                        p_re_list = []
                        tw_re_list = []
                        tw_sup_list = []
                        hp_state_list = []
                    
                        # VFD states
                        try:
                            data_vfd_onoff = db_read(cursor, 'pump_vfd_his', 'pump_onoff_feedback', step_length)
                            data_vfd_frequency = db_read(cursor, 'pump_vfd_his', 'pump_frequency_feedback', step_length)
                            for p in range(0, step_length):
                                if data_vfd_onoff[step_length-1-p][3] != 'vfd_onoff_state err':
                                    vfd_onoff = int(data_vfd_onoff[step_length-1-p][3])
                                    break
                            for p in range(0, step_length):
                                if data_vfd_frequency[step_length-1-p][3] != 'vfd_frequency err':
                                    vfd_frequency = float(data_vfd_frequency[step_length-1-p][3])
                                    break
                        except Exception as err1:
                            self.sendDatatoGUI("VFD states reading error: " + str(err1))
                        # IO state lists
                        try:
                            # 读不够step_length会报错
                            data_outdoor_temp = db_read(cursor, 'sensor_outdoor_his', 'outdoor_temp', step_length)
                            data_p_sup = db_read(cursor, 'sensor_pressure_his', 'supply_pressure', step_length)
                            data_p_re = db_read(cursor, 'sensor_pressure_his', 'return_pressure', step_length)
                            data_tw_re = db_read(cursor, 'sensor_watertemp_his', 'return_temp', step_length)
                            for s in range(step_length):
                                outdoor_temp_list.append(float(data_outdoor_temp[step_length-s-1][3]))
                                p_sup_list.append(float(data_p_sup[step_length-s-1][3]))
                                p_re_list.append(float(data_p_re[step_length-s-1][3]))
                                tw_re_list.append(float(data_tw_re[step_length-s-1][3]))
                        except Exception as err2:
                            self.sendDatatoGUI("IO states reading error: " + str(err2))
                        # Heatpump states - need data transport(list)
                        # 阻塞性地获取数据
                        self.sendDataToDescendant('apply heatpump data', path[:])
                        data, __, __ = self.descendantData.get()
                        hp_state_list,tw_sup_list = data

                        # Control
                        vfd_onoff_con = 1
                        if step_count % step_length == 0:
                            # Control algorithms
                            try:
                                avg_tw_re = np.mean(tw_re_list)
                                avg_tw_sup = np.mean(tw_sup_list)
                                avg_dtw = avg_tw_re - avg_tw_sup
                                self.sendDatatoGUI('vfd_frequency:{}  avg_tw_re:{} avg_tw_sup:{} avg_dtw:{}'.format(vfd_frequency, avg_tw_re, avg_tw_sup, avg_dtw))
                                vfd_frequency_con = pump_control_cooling(vfd_frequency, tw_re_list, tw_sup_list)
                                step_count += 1
                            except Exception as err4:
                                self.sendDatatoGUI("Control algorithm error: " + str(err4))
                        self.sendDatatoGUI('step:{} pump_onoff_setpoint:{}  pump_frequency_setpoint:{}'.format(step, vfd_onoff_con, vfd_frequency_con))
                        db_operate(cursor, 'pump_vfd_control', db_time, '0x24000208', 'pump_onoff_setpoint', str(vfd_onoff_con), step)
                        db_operate(cursor, 'pump_vfd_control', db_time, '0x24000216', 'pump_frequency_setpoint', str(vfd_frequency_con), step)
                        step += 1
                       
                    else:
                        vfd_onoff_con = 0
                        step_count = 0
                        self.sendDatatoGUI('step:{} pump_onoff_setpoint:{}  pump_frequency_setpoint:{}'.format(step, vfd_onoff_con, vfd_frequency_con))
                        db_operate(cursor, 'pump_vfd_control', db_time, '0x24000208', 'pump_onoff_setpoint', str(vfd_onoff_con), step)
                        db_operate(cursor, 'pump_vfd_control', db_time, '0x24000216', 'pump_frequency_setpoint', str(vfd_frequency_con), step)
                    # Write db

                     
            except Exception as cerr:
                self.sendDatatoGUI("Pump control shell error: " + str(cerr))

            db.commit()
                            
            if (datetime.now()-zero_time).days > 0:
                clear_con_db(db, 2)
                step = 0
                cur_date = datetime.now().strftime("%Y%m%d")
                zero_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 0, 0)
            self.sendDatatoGUI("Control shell working!")

            end_time = datetime.now()
            if (end_time-start_time).seconds < 60:
                time.sleep(60 - (end_time-start_time).seconds)

    elif id[:4] == "heat":
        db = pymysql.connect(host="localhost", user="root", passwd="cfins", db="data", charset='utf8')
        cursor = db.cursor()
        step_length = 20            # transport to hp node or sync to hp node
        self.sendDataToRoot("send heatpump path")
        while True:
            if not self.rootData.empty():
                # 非阻塞性地获取数据
                # data: 后代节点数据
                # path: 后代节点发送过来的路径，发送的节点在首位
                # recvtime: 接受到消息的时刻
                data, __ = self.rootData.get_nowait()
                self.sendDatatoGUI("接收到水泵节点的数据请求")
                try:
                    tw_sup_list = []
                    hp_state_list = []
                    data_hp_state = db_read(cursor, 'heatpump_panel_his', 'heatpump_workingmode_feedback', step_length)
                    data_tw_sup = db_read(cursor, 'heatpump_panel_his', 'heatpump_supplytemp_feedback', step_length)
                    for s in range(step_length):
                        hp_state_list.append(int(data_hp_state[step_length-s-1][3]))
                        tw_sup_list.append(float(data_tw_sup[step_length-s-1][3]))
                except Exception as err3:
                    self.sendDatatoGUI("Heatpump states reading error: " + str(err3))
                else:
                    # 发送给后代节点时根据path传输，若path为空则进行广播
                    self.sendDataToRoot([hp_state_list,tw_sup_list])
                    self.sendDatatoGUI("热泵节点成功发送数据")
            else:
                time.sleep(0.01)