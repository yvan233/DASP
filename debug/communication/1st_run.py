# coding=utf-8

import time
import os
import pymysql
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus_protocol.inspect_ports import *
from pymodbus_protocol.IO_mod import *
from pymodbus_protocol.FCU_panel import *
from datetime import datetime

def clear_db(db, mode):
    cursor = db.cursor()
    sql = "SELECT database()"
    cursor.execute(sql)
    dbname = cursor.fetchall()[0][0]
    sql = '''SELECT 
                    table_name 
                FROM
                    information_schema.TABLES 
                WHERE 
                    table_schema = '%s'
        ''' % (dbname)
    cursor.execute(sql)
    data = cursor.fetchall()
    for l in range(len(data)):
        if mode == 1:
            sql = "TRUNCATE TABLE %s" % (data[l][0])
            cursor.execute(sql)
        elif mode == 2:
            if data[l][0][-4:] != '_his' and data[l][0][-7:] != 'control':
                sql = "TRUNCATE TABLE %s" % (data[l][0])
                cursor.execute(sql)
    db.commit()


def db_insert(cursor, table, time, id ,name, value):
    sql = "INSERT INTO %s(time, id ,name, value) VALUES ('%s', '%s', '%s', '%s')" % (table, time, id, name, value)
    cursor.execute(sql)

def db_update(cursor, table, time, name, value):
    sql = "UPDATE %s SET time='%s', value='%s' WHERE name='%s'" % (table, time, value, name)
    cursor.execute(sql)

def db_read(cursor, table, name, num):               # num 为倒序读取数据条目数，0表示读取全部
    if num == 0:
        sql = "SELECT %s, %s, %s, %s FROM %s WHERE name='%s'" % ('time', 'id', 'name', 'value', table, name)
        cursor.execute(sql)
        data = cursor.fetchall()
    else:
        sql = "SELECT %s, %s, %s, %s FROM %s WHERE name='%s' order by time DESC limit %d" % ('time', 'id', 'name', 'value', table, name, num)
        cursor.execute(sql)
        data = cursor.fetchall()
    return data

def db_operate(cursor, table, time, id ,name, value, step_num):
    db_insert(cursor, table + '_his', time, id, name, value)
    if step_num == 0:
        db_insert(cursor, table, time, id, name, value)
    else:
        db_update(cursor, table, time, name, value)

class CONTROLJUDGE():
    def __init__(self, t_pro):
        self.t = 0
        self.t_pro = t_pro
        self.flag = 0
    
    def control_judge(self, data_his, data_control, data_controlmode, type = 'int'):
        # 转换历史数据
        if type == 'int':
            feedback_t = int(data_his[0][3])
            feedback_t_last = int(data_his[1][3])
        else:
            feedback_t = float(data_his[0][3])
            feedback_t_last = float(data_his[1][3])

        # 维护计时器
        if feedback_t_last != feedback_t and self.flag == 0:        # 存在非算法的外部输入
            self.t = self.t_pro                  # 维持外部输入for t_pro
        elif self.t > 0:    
            self.t -= 1

        if data_controlmode:
            # 转换控制信号
            control_mode = int(data_controlmode[0][3]) 
            if type == 'int':
                control_signal = int(data_control[0][3])
            else:
                control_signal = float(data_control[0][3]) 

            if control_mode == 0:    # 纯手动
                pass
            elif control_mode == 1:  # 纯自动
                if feedback_t != control_signal:       # 算法控制指令与本地反馈值不同                              
                    return control_signal                # 触发控制指令
            else:                    # 手自动混合(保护手动)
                if self.t == 0 and feedback_t != control_signal:
                    return control_signal
        return None
    
    def mandatory_control(self):                     # 移除手动保持时间
        self.t = 0


if __name__ == '__main__':
    # 端口巡检
    port1, port2 = port_inspect()
    # 实例化
    io = IO(port1)
    fcu = FCU(port2, 4800)
    t_pro = 60     # 用户输入后保护时间, min
    onoff_judge = CONTROLJUDGE(t_pro)
    tset_judge = CONTROLJUDGE(t_pro)
    mode_judge = CONTROLJUDGE(t_pro)
    fan_judge = CONTROLJUDGE(t_pro)

    # db connection
    db = pymysql.connect(host="localhost", user="root", passwd="cfins", db="data", charset='utf8')
    cursor = db.cursor()

    cur_date = datetime.now().strftime("%Y%m%d")
    zero_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 0, 0)
    if (datetime.now()-zero_time).days == 0:
        clear_db(db, 2)
        step = 0
    elif (datetime.now()-zero_time).days > 0:
        os.system("python3 " + os.getcwd() + "/db_backup.py")
        clear_db(db, 1)
        step = 0
        cur_date = datetime.now().strftime("%Y%m%d")
        zero_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 0, 0)

    while True:
        start_time = datetime.now()       # 单轮循环计时
        db_time = start_time.strftime("%Y-%m-%d %H:%M:%S")        
        try:
            # 频率为1min的采样
            # read 
            print("time = " + db_time)
            io.read_registers()
            io.value_transform()
            #io.value_print()
            fcu.read_registers()
            fcu.value_transform()
            #fcu.value_print()

            # 室内温度
            if io.temp1 > 0:
                # 若成功，写入数据库
                db_operate(cursor, 'sensor_room', db_time, '0x00000220', 'room_temp1', str(io.temp1), step)
                db_operate(cursor, 'sensor_room', db_time, '0x00000222', 'room_temp2', str(io.temp1), step)
            else:
                # 若失败，写入报错信息
                db_operate(cursor, 'sensor_room', db_time, '0x00000220', 'room_temp1', "temp1_error", step)
                db_operate(cursor, 'sensor_room', db_time, '0x00000222', 'room_temp2', "temp2_error", step)

            # 室内湿度
            if io.rh1 > 0:
                # 若成功，写入数据库
                db_operate(cursor, 'sensor_room', db_time, '0x00000221', 'room_RH1', str(io.rh1), step)
                db_operate(cursor, 'sensor_room', db_time, '0x00000223', 'room_RH2', str(io.rh1), step)
            else:
                # 若失败，写入报错信息
                db_operate(cursor, 'sensor_room', db_time, '0x00000221', 'room_RH1', "rh1_error", step)
                db_operate(cursor, 'sensor_room', db_time, '0x00000223', 'room_RH2', "rh2_error", step)

            # 室内压差传感器
            if io.dp:
                db_operate(cursor, 'sensor_room', db_time, '0x00000425', 'differential_pressure', str(io.dp), step)
            else:
                db_operate(cursor, 'sensor_room', db_time, '0x00000425', 'differential_pressure', "dp_error", step)

            # FCU 传感器
            # 压力传感器
            if io.p1 != 'p_err':
                db_operate(cursor, 'sensor_fcu_waterflow', db_time, '0x00000420', 'supply_pressure', str(io.p1), step)
            else:
                db_operate(cursor, 'sensor_fcu_waterflow', db_time, '0x00000420', 'supply_pressure', 'P_sup error', step)

            if io.p2 != 'p_err':
                db_operate(cursor, 'sensor_fcu_waterflow', db_time, '0x00000421', 'return_pressure', str(io.p2), step)
            else:
                db_operate(cursor, 'sensor_fcu_waterflow', db_time, '0x00000421', 'return_pressure', 'P_re error', step)

            #温度传感器
            if io.tw_sup >=0 and io.tw_sup <= 100:
                db_operate(cursor, 'sensor_fcu_watertemp', db_time, '0x00000422', 'supply_temp', str(io.tw_sup), step)
            else:
                db_operate(cursor, 'sensor_fcu_watertemp', db_time, '0x00000422', 'supply_temp', 'tw_sup error', step)
            
            if io.tw_re >= 0 and io.tw_re <= 100:
                db_operate(cursor, 'sensor_fcu_watertemp', db_time, '0x00000423', 'return_temp', str(io.tw_re), step)
            else:
                db_operate(cursor, 'sensor_fcu_watertemp', db_time, '0x00000423', 'return_temp', 'tw_re error', step)

            # 流量传感器
            if io.f >= 0 and io.f <= 7.0:
                db_operate(cursor, 'sensor_fcu_waterflow', db_time, '0x00000424', 'waterflow', str(io.f), step)
            else:
                db_operate(cursor, 'sensor_fcu_waterflow', db_time, '0x00000424', 'waterflow', 'flow error', step)
            
            # alarming
            if io.temp1 > 30:
                db_operate(cursor, 'alarm', db_time, '0x00001000', 'room_temp_alarm', '室温过高', step)
            elif io.temp1 < 18:
                db_operate(cursor, 'alarm', db_time, '0x00001000', 'room_temp_alarm', '室温过低', step)

            # 读fcu反馈并写入数据库
            # 启停状态
            #print("onoff_feedback: " + str(fcu.on_off))
            if fcu.on_off == 0 or fcu.on_off == 1:
                db_operate(cursor, 'fcu_panel', db_time, '0x00000410', 'FCU_onoff_feedback', str(fcu.on_off), step)
            else:
                db_operate(cursor, 'fcu_panel', db_time, '0x00000410', 'FCU_onoff_feedback', 'FCU_on_off_error', step)
            
            # 面板锁状态
            #print("FCU_lock_state: " + str(fcu.lock_state))
            db_operate(cursor, 'fcu_panel', db_time, '0x00000411', 'FCU_lock_feedback', str(fcu.lock_state), step)
            
            # 温度设定
            #print("set_point: " + str(fcu.set_point))
            if fcu.set_point:
                db_operate(cursor, 'fcu_panel', db_time, '0x00000240', 'FCU_temp_setpoint', str(fcu.set_point), step)
            else:
                db_operate(cursor, 'fcu_panel', db_time, '0x00000240', 'FCU_temp_setpoint', 'FCU_setpoint_error', step)
            
            # 面板温度传感器
            if fcu.indoor_temp:
                db_operate(cursor, 'fcu_panel', db_time, '0x00000241', 'FCU_temp_feedback', str(fcu.indoor_temp), step)
            else:
                db_operate(cursor, 'fcu_panel', db_time, '0x00000241', 'FCU_temp_feedback', 'FCU_temp_error', step)

            # 风机档位 0-auto, 1-high, 2-medium, 3-low
            fan_state = fan_read_modify(5, fcu.fan)                      
            #print("fan_feecback: " + str(fan_state))
            if fan_state in [0,1,2,3]:
                db_operate(cursor, 'fcu_panel', db_time, '0x00000412', 'FCU_fan_feedback', str(fan_state), step)
            else:
                db_operate(cursor, 'fcu_panel', db_time, '0x00000412', 'FCU_fan_feedback', 'fcu_fan_error', step)

            # 工作模式
            #print("mode: " + str(fcu.mode))
            if fcu.mode in [1,2,3]:
                db_operate(cursor, 'fcu_panel', db_time, '0x00000418', 'FCU_mode_feedback', str(fcu.mode), step)
            else:
                db_operate(cursor, 'fcu_panel', db_time, '0x00000418', 'FCU_mode_feedback', 'fcu_mode_error', step)
            time.sleep(1)

            # 手动输入状态： 0 - 自动控制， >0 - 手动控制保护倒计时
            db_operate(cursor, 'fcu_panel', db_time, '0x00000600', 'manul_FCU_onoff', str(onoff_judge.t), step)
            db_operate(cursor, 'fcu_panel', db_time, '0x00000601', 'manul_temp_setpoint', str(tset_judge.t), step)
            db_operate(cursor, 'fcu_panel', db_time, '0x00000602', 'manul_FCU_fan', str(fan_judge.t), step)
            db_operate(cursor, 'fcu_panel', db_time, '0x00000603', 'manul_FCU_mode', str(mode_judge.t), step)

            try:
                # 读历史反馈
                data_tset_his = db_read(cursor, 'fcu_panel_his', 'FCU_temp_setpoint', 2)
                data_fcuonoff_his = db_read(cursor, 'fcu_panel_his', 'FCU_onoff_feedback', 2)
                data_fcumode_his = db_read(cursor, 'fcu_panel_his', 'FCU_mode_feedback', 2)
                data_fcufan_his = db_read(cursor, 'fcu_panel_his', 'FCU_fan_feedback', 2)

                # 读控制指令
                data_tset = db_read(cursor, 'fcu_control', 'FCU_temp_setpoint', 0)
                data_onoff = db_read(cursor, 'fcu_control', 'FCU_onoff_setpoint', 0)
                data_mode = db_read(cursor, 'fcu_control', 'FCU_mode_setpoint', 0)
                data_fan = db_read(cursor, 'fcu_control', 'FCU_fan_setpoint', 0)

                # 读控制模式   0纯手动  1纯自动  2手自动混合(保护手动)
                data_controlmode = db_read(cursor, 'fcu_control', 'FCU_control_mode', 0)

            except Exception as err1:
                print("Control read db error: " + str(err1))
            else:
                try:
                    # 控制指令判断
                    onoff_set = onoff_judge.control_judge(data_fcuonoff_his, data_onoff, data_controlmode, 'int')
                    t_set = tset_judge.control_judge(data_tset_his, data_tset, data_controlmode, 'float')
                    mode_set = mode_judge.control_judge(data_fcumode_his, data_mode, data_controlmode, 'int')
                    fan_set = fan_judge.control_judge(data_fcufan_his, data_fan, data_controlmode, 'int')

                    # 控制设备
                    if onoff_set != None:
                        fcu.set_onoff(onoff_set)
                        onoff_judge.flag = 1
                        time.sleep(5)
                    else:
                        onoff_judge.flag = 0
                    if mode_set != None:
                        fcu.set_mode(mode_set)
                        mode_judge.flag = 1
                        time.sleep(5)
                    else:
                        mode_judge.flag = 0
                    if t_set != None:
                        fcu.set_temp_point(t_set)
                        tset_judge.flag = 1
                        time.sleep(5)
                    else:
                        tset_judge.flag = 0
                    if fan_set != None:
                        fan_write = fan_write_modify(5, fan_set)          
                        fcu.set_fan(fan_write)
                        fan_judge.flag = 1
                        time.sleep(5)
                    else:
                        fan_judge.flag = 0
                    print('FCU control succeed!')
                except Exception as cerr:
                    print('FCU control failed! error: ' + str(cerr))
            
            db.commit()
            step += 1
        except Exception as err:
            print("Node shell work error with " + str(err))
        
        db.commit()
        # backup and clear db
        if (datetime.now()-zero_time).days > 0:
            os.system("python3 " + os.getcwd() + "/db_backup.py")
            clear_db(db, 1)
            step = 0
            cur_date = datetime.now().strftime("%Y%m%d")
            zero_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 0, 0)
            onoff_judge.t = 0
            tset_judge.t = 0
            mode_judge.t = 0
            fan_judge.t = 0

        print("Node working!")
        end_time = datetime.now()
        if (end_time-start_time).seconds < 60:
            time.sleep(60 - (end_time-start_time).seconds)