# 时间同步APP
import time
import os
import pymysql
from datetime import datetime,timedelta
from .db_operations import *
from .basic_functions import *
    

def taskFunction(self, id, adjDirection, datalist):
    if id[:4] == "room":
        # db connection
        db = pymysql.connect(host="localhost", user="root", passwd="cfins", db="data", charset='utf8')
        cursor = db.cursor()

        cur_date = datetime.now().strftime("%Y%m%d")
        zero_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 0, 0)
        clear_con_db(db, 2)
        step = 0
        occ_onoff = 0
        while True:
            start_time = datetime.now()
            db_time = start_time.strftime("%Y-%m-%d %H:%M:%S") 
            try:
                cur_weekday = start_time.strftime("%A")        # 当前星期
                cur_date = datetime.now().strftime("%Y%m%d")               # 当前日期
                auto_start_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 9, 0)       
                auto_stop_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 17, 30)     
                stop_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 18, 00)   

                if cur_weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:      # 工作日
                    if datetime.now() > auto_start_time and  datetime.now() <= auto_stop_time:    # 启停时间内
                        # Read occ list
                        try:
                            occ_length = 5
                            occ_list = []
                            data_occ = db_read(cursor, 'sensor_occupant_his', 'occupant_num', occ_length)
                            if len(data_occ) == occ_length:
                                for o in range(occ_length):
                                    occ_list.append(int(data_occ[occ_length-1-o][3])) #  最后一个数值为最近时刻人数，首个数值为occ_length之前时刻人数
                                # self.sendDatatoGUI("occ_list: "+str(occ_list))
                            else:
                                self.sendDatatoGUI("occ_length not enough.")
                        except Exception as oerr:
                            self.sendDatatoGUI("occ read err: " + str(oerr))
                        
                        # Read states
                        # temperature
                        try:
                            data_temp1 = db_read(cursor, 'sensor_room', 'room_temp1', 0)
                            room_temp1 = float(data_temp1[0][3])
                            data_temp2 = db_read(cursor, 'sensor_room', 'room_temp2', 0)
                            room_temp2 = float(data_temp2[0][3])
                            room_temp = 0.5 * (room_temp1 + room_temp2)
                            time.sleep(1)
                        except:
                            self.sendDatatoGUI("Temperature reading failed!")
                        
                        # FCU state
                        try:
                            data_fcu_onoff = db_read(cursor, 'fcu_panel', 'FCU_onoff_feedback', 0)
                            data_temp_sp = db_read(cursor, 'fcu_panel', 'FCU_temp_setpoint', 0)
                            data_fcu_mode = db_read(cursor, 'fcu_panel', 'FCU_mode_feedback', 0)
                            data_fcu_fan = db_read(cursor, 'fcu_panel', 'FCU_fan_feedback', 0)
                            fcu_onoff_state = int(data_fcu_onoff[0][3])
                            temp_sp = float(data_temp_sp[0][3])
                            fcu_mode = int(data_fcu_mode[0][3])
                            fcu_fan = int(data_fcu_fan[0][3])
                        except:
                            self.sendDatatoGUI("FCU reading failed!")
                        
                        # Control judge
                        # Condition judge
                        
                        if int(cur_date[4:6]) in [6,7,8,9]:
                            condition = 'cooling'
                        elif int(cur_date[4:6]) in [1,2,11,12]:
                            condition = 'heating'
                        else:
                            condition = 'ventilation'

                        if condition == 'cooling':
                            try:
                                con_fcu_mode = 1
                                # Set point judge
                                if temp_sp < 25.0:
                                    con_temp_sp = 25.0
                                elif temp_sp > 27.0:
                                    con_temp_sp = 27.0
                                else:
                                    con_temp_sp = temp_sp
                                # occ judge
                                # if occ_list[-1] > 0 and occ_list[-2] > 0:
                                #     occ_onoff = 1
                                # elif any(occ_list) == False:
                                #     occ_onoff = 0
                                if any(occ_list):
                                    occ_onoff = 1
                                else:
                                    occ_onoff = 0
                                con_fan = cal_fcu_fan_cooling(temp_sp, room_temp, fcu_fan, occ_onoff)
                                if con_fan == 0:
                                    con_onoff = 0
                                else:
                                    con_onoff = 1
                            except Exception as err:
                                self.sendDatatoGUI('Control judge err: ' + str(err))
                                con_fan = None
                                con_onoff = None
                        
                        elif condition == 'heating':
                            try:
                                con_fcu_mode = 2
                                # Set point judge
                                if temp_sp < 18.0:
                                    con_temp_sp = 18.0
                                elif temp_sp > 25.0:
                                    con_temp_sp = 25.0
                                else:
                                    con_temp_sp = temp_sp
                                # occ judge

                                if occ_list[-1] > 0 and occ_list[-2] > 0:
                                    occ_onoff = 1
                                elif any(occ_list) == False:
                                    occ_onoff = 0
                                con_fan = cal_fcu_fan_heating(temp_sp, room_temp, fcu_fan, occ_onoff)
                                if con_fan == 0:
                                    con_onoff = 0
                                else:
                                    con_onoff = 1
                            except Exception as err:
                                self.sendDatatoGUI('Control judge err: ' + str(err))
                                con_fan = None
                                con_onoff = None
                        
                        # Write db
                        try:
                            self.sendDatatoGUI('FCU_temp_setpoint:{}  FCU_onoff_setpoint:{}  FCU_mode_setpoint:{} FCU_fan_setpoint:{}'\
                                .format(con_temp_sp, con_onoff, con_fcu_mode, con_fan))
                            db_operate(cursor, 'fcu_control', db_time, '0x00000410', 'FCU_temp_setpoint', str(con_temp_sp), step)
                            db_operate(cursor, 'fcu_control', db_time, '0x00000411', 'FCU_onoff_setpoint', str(con_onoff), step)
                            db_operate(cursor, 'fcu_control', db_time, '0x00000419', 'FCU_mode_setpoint', str(con_fcu_mode), step)
                            db_operate(cursor, 'fcu_control', db_time, '0x00000413', 'FCU_fan_setpoint', str(con_fan), step)
                            
                        except Exception as derr:
                            self.sendDatatoGUI('Control signal write err: ' + str(derr))
                        db.commit()
                        step += 1  

                    elif datetime.now() > stop_time and  datetime.now() <= stop_time + timedelta(minutes = 1):
                        self.sendDatatoGUI('FCU_temp_setpoint:{}  FCU_onoff_setpoint:{}  FCU_mode_setpoint:{} FCU_fan_setpoint:{}'\
                            .format(25, 0, con_fcu_mode, con_fan))
                        db_operate(cursor, 'fcu_control', db_time, '0x00000410', 'FCU_temp_setpoint', 25, 0)
                        db_operate(cursor, 'fcu_control', db_time, '0x00000411', 'FCU_onoff_setpoint', 0, 0)
                        db_operate(cursor, 'fcu_control', db_time, '0x00000419', 'FCU_mode_setpoint', 1, 0)
                        db_operate(cursor, 'fcu_control', db_time, '0x00000413', 'FCU_fan_setpoint', 'M', 0)
                    else:
                        cjudge = db_read(cursor, 'fcu_control', 'FCU_onoff_setpoint', 0)
                        if cjudge:
                            clear_con_db(db, 2)

            except Exception as cerr:
                self.sendDatatoGUI('Control process err: ' + str(cerr))
            
            end_time = datetime.now()
            if (end_time-start_time).seconds < 60:
                time.sleep(60 - (end_time-start_time).seconds)

            if (datetime.now()-zero_time).days > 0:
                clear_con_db(db, 2)
                step = 0
                cur_date = datetime.now().strftime("%Y%m%d")
                zero_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 0, 0)
            print("Control shell working!")