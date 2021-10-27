import time
import pymysql
from datetime import datetime
from db_operations import *
from control_functons import *

if __name__ == '__main__':
    # db connection
    db = pymysql.connect(host="localhost", user="root", passwd="cfins", db="data", charset='utf8')
    cursor = db.cursor()

    cur_date = datetime.now().strftime("%Y%m%d")
    zero_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 0, 0)
    if (datetime.now()-zero_time).days == 0:
        clear_con_db(db, 2)
        step = 0
    elif (datetime.now()-zero_time).days > 0:
        clear_con_db(db, 2)
        step = 0
        cur_date = datetime.now().strftime("%Y%m%d")
        zero_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 0, 0)
    
    vfd_frequency_con = 40.0
    step_length = 20            # transport to hp node or sync to hp node
    step_count = 0
    
    while True:
        start_time = datetime.now()
        db_time = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            # 定时开关机
            cur_weekday = time.strftime("%A", time.localtime())        # 当前星期
            cur_date = datetime.now().strftime("%Y%m%d")
            auto_open_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 7, 50)       # 自动开机时间 
            auto_close_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 18, 10)     # 自动关机时间

            if cur_weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:      # 工作日
                if (datetime.now()-auto_open_time).days == 0 and (datetime.now()-auto_close_time).days == -1:    # 启停时间内
                    # Read states
                    outdoor_temp_list = []
                    p_sup_list = []
                    p_re_list = []
                    tw_re_list = []
                    tw_sup_list = []
                    hp_state_list = []

                    # VFD states
                    try:
                        data_vfd_onoff = db.read(cursor, 'pump_vfd', 'pump_onoff_feedback', 0)
                        data_vfd_frequency = db.read(cursor, 'pump_vfd', 'pump_frequency_feedback', 0)
                        vfd_onoff = int(data_vfd_onoff[0][3])
                        vfd_frequency = int(data_vfd_frequency[0][3])
                    except Exception as err1:
                        print("VFD states reading error: " + str(err1))
                    # IO state lists
                    try:
                        data_outdoor_temp = db.read(cursor, 'sensor_outdoor_his', 'outdoor_temp', step_length)
                        data_p_sup = db.read(cursor, 'sensor_pressure_his', 'supply_pressure', step_length)
                        data_p_re = db.read(cursor, 'sensor_pressure_his', 'return_pressure', step_length)
                        data_tw_re = db.read(cursor, 'sensor_watertemp_his', 'return_temp', step_length)
                        for s in range (0, step_length):
                            outdoor_temp_list.append(float(data_outdoor_temp[step_length-s-1][3]))
                            p_sup_list.append(float(data_p_sup[step_length-s-1][3]))
                            p_re_list.append(float(data_p_re[step_length-s-1][3]))
                            tw_re_list.append(float(data_tw_re[step_length-s-1][3]))
                    except Exception as err2:
                        print("IO states reading error: " + str(err2))
                    # Heatpump states - need data transport(list)
                    '''
                    try:
                        hp_state_list = transported hp list    # same as the above IO state lists
                        tw_sup_list = transported tsup list
                    except Exception as err3:
                        print("Heatpump states reading error: " + str(err3))
                    '''

                    # Control
                    vfd_onoff_con = 1
                    if step_count % step_length == 0:
                        # Control algorithms
                        try:
                            vfd_frequency_con = pump_control_cooling(vfd_frequency, tw_re_list, tw_sup_list)
                            step_count += 1
                        except Exception as err4:
                            print("Control algorithm error: " + str(err4))
                    step += 1
                    
                else:
                    vfd_onoff_con = 0
                    step_count = 0
                
                # Write db
                db_operate(cursor, 'pump_vfd_control', db_time, '0x24000208', 'pump_onoff_setpoint', str(vfd_onoff_con), step)
                db_operate(cursor, 'pump_vfd_control', db_time, '0x24000216', 'pump_frequency_setpoint', str(vfd_frequency_con), step)
        
        except Exception as cerr:
            print("Pump control shell error: " + str(cerr))
        
        end_time = datetime.now()
        if (end_time-start_time).seconds < 60:
            time.sleep(60 - (end_time-start_time).seconds)
            
        if (datetime.now()-zero_time).days > 0:
            clear_con_db(db, 2)
            step = 0
            cur_date = datetime.now().strftime("%Y%m%d")
            zero_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 0, 0)
        print("Control shell working!")