# coding=utf-8
import time
import pymysql
import math
import numpy as np
# 计算风机盘管挡位
def cal_fcu_fan(tem_s, tem_k, position_k):
    H = 3
    M = 2
    L = 1
    Off = 0
    a1 = 0.5
    a2 = 1
    a3 = 2
    a4 = 3
    position_s = 0
    if tem_s - tem_k > a4:
        position_s = H
    elif a3 <= tem_s - tem_k < a4 and (position_k == M):
        position_s = M
    elif a3 < tem_s - tem_k <= a4 and (position_k == H):
        position_s = H
    elif a3 < tem_s - tem_k <= a4 and (position_k == L):
        position_s = M
    elif a2 < tem_s - tem_k <= a3:
        position_s = M
    elif a1 <= tem_s - tem_k < a2 and (position_k == L):
        position_s = L
    elif a1 < tem_s - tem_k <= a2 and (position_k == M):
        position_s = M
    elif a1 < tem_s - tem_k <= a2 and (position_k == H):
        position_s = M
    elif -a2 < tem_s - tem_k <= a1:
        position_s = L
    # elif -a4 <tem_s - tem_k <= -a2 and (position_k == L):
    #     position_s = L
    elif -a4 < tem_s - tem_k <= -a2 and (position_k == L or position_k == M or position_k == H):
        position_s = L
    elif -a4 < tem_s - tem_k <= -a2 and (position_k == Off):
        position_s = Off
    elif -a4 < tem_s - tem_k <= -a2 and (position_k == Off):
        position_s = Off
    elif tem_s - tem_k <= -a4:
        position_s = Off
    return position_s

# 本地水泵需求预测
def pre_Q(temp_list, f_list, tws_list, twr_list, position_s, tem_s):
    pre_length = len(f_list)
    Qw1 = 0
    Qw2 = 0

    for l in range(0, pre_length):
        if l < (0.5 * pre_length):
            Qw1 += 4.2 * 1000 * f_list[l] / 60 * (tws_list[l] - twr_list[l])
        else:
            Qw2 += 4.2 * 1000 * f_list[l] / 60 * (tws_list[l] - twr_list[l])

    if position_s > 0:
        dt1 = temp_list[int(0.5 * pre_length - 1)] - temp_list[0]
        dt2 = temp_list[-1] - temp_list[int(0.5 * pre_length)]
        dt_demand = tem_s - temp_list[-1]
        if abs(dt1 - dt2) > 0.2:
            k = (Qw1 - Qw2) / (dt1 - dt2)          #  room heat constant (approximate)
        else:
            k = (Qw1 - Qw2) / 0.2 * np.sign(dt1 - dt2)
        #pQ = Qw2 + math.exp(-1) * k * (dt_demand - dt2)
        pQ = Qw2 + k * (dt_demand - dt2)
    else:
        pQ = Qw2
    return pQ,Qw2

# 读本地参数
def R_room_node(db):
    cursor = db.cursor()
    sql = "SELECT %s, %s, %s, %s FROM sensor_room" % ('time', 'id', 'name', 'value')
    cursor.execute(sql)
    data1 = cursor.fetchall()
    if data1:
        for i in range (0, 2):
            if data1[i][2] == 'room_temp':
                tem_k = float(data1[i][3])
    else:
        tem_k = 18.0
    sql = "SELECT %s, %s, %s, %s FROM fcu_panel" % ('time', 'id', 'name', 'value')
    cursor.execute(sql)
    data2 = cursor.fetchall()
    if data2:
        for i in range (0, 6):
            if data2[i][2] == 'roomtemp_setpoint':
                tem_s = float(data2[i][3])
            if data2[i][2] == 'FCU_fan_feedback':
                position_k = float(data2[i][3])
    else:
        tem_s = 24.0
        position_k = 1
    return tem_s, tem_k, position_k


def R_room_his(db, length, step_min):      #  read his data
    temp_list = np.zeros(length)
    f_list = np.zeros(length)
    tws_list = np.zeros(length)
    twr_list = np.zeros(length)

    if step_min > length:
        cursor = db.cursor()
        sql = "SELECT %s, %s, %s, %s FROM sensor_room_his WHERE name='room_temp' order by time DESC limit %d" % \
              ('time', 'id', 'name', 'value', length)
        cursor.execute(sql)
        temp_data = cursor.fetchall()
        sql = "SELECT %s, %s, %s, %s FROM sensor_fcu_waterflow_his order by time DESC limit %d" % \
              ('time', 'id', 'name', 'value', length)
        cursor.execute(sql)
        f_data = cursor.fetchall()
        sql = "SELECT %s, %s, %s, %s FROM sensor_fcu_watertemp_his WHERE name='supply_temp' order by time DESC limit %d" % \
              ('time', 'id', 'name', 'value', length)
        cursor.execute(sql)
        tws_data = cursor.fetchall()
        sql = "SELECT %s, %s, %s, %s FROM sensor_fcu_watertemp_his WHERE name='return_temp' order by time DESC limit %d" % \
              ('time', 'id', 'name', 'value', length)
        cursor.execute(sql)
        twr_data = cursor.fetchall()

        for i in range(0, length):
            temp_list[length - 1 - i] = float(temp_data[i][3])
            f_list[length - 1 - i] = float(f_data[i][3])
            tws_list[length - 1 - i] = float(tws_data[i][3])
            twr_list[length - 1 - i] = float(twr_data[i][3])
    return temp_list, f_list, tws_list, twr_list


# 写本地node
def W_room_node_control(db, time, onoff, fan_set, mode, valve_set, pQ):
    cursor = db.cursor()
    sql = "INSERT INTO fcu_control_his(time, id ,name, value) VALUES (%d, '%s', '%s', %.1f)" % \
          (time, '0x00000411', 'FCU_onoff_setpoint', onoff)
    cursor.execute(sql)
    sql = "INSERT INTO fcu_control_his(time, id ,name, value) VALUES (%d, '%s', '%s', %.1f)" % \
          (time, '0x00000413', 'FCU_fan_setpoint', fan_set)
    cursor.execute(sql)
    sql = "INSERT INTO fcu_control_his(time, id ,name, value) VALUES (%d, '%s', '%s', %.1f)" % \
          (time, '0x00000419', 'FCU_workingmode_setpoint', mode)
    cursor.execute(sql)
    sql = "INSERT INTO fcu_valve_control_his(time, id ,name, value) VALUES (%d, '%s', '%s', %.1f)" % \
          (time, '0x00000425', 'valve_setpoint', valve_set)
    cursor.execute(sql)
    sql = "INSERT INTO fcu_valve_control_his(time, id ,name, value) VALUES (%d, '%s', '%s', %.1f)" % \
          (time, '0x00000426', 'pre_Q', pQ)
    cursor.execute(sql)
    sql = "SELECT %s, %s, %s, %s FROM fcu_control" % ('time', 'id', 'name', 'value')
    cursor.execute(sql)
    data = cursor.fetchall()
    if data:
        sql = "UPDATE fcu_control SET time=%d, value=%.1f WHERE name='%s'" % (time, onoff, 'FCU_onoff_setpoint')
        cursor.execute(sql)
        sql = "UPDATE fcu_control SET time=%d, value=%.1f WHERE name='%s'" % (time, fan_set, 'FCU_fan_setpoint')
        cursor.execute(sql)
        sql = "UPDATE fcu_control SET time=%d, value=%.1f WHERE name='%s'" % (time, mode, 'FCU_workingmode_setpoint')
        cursor.execute(sql)
        sql = "UPDATE fcu_valve_control SET time=%d, value=%.1f WHERE name='%s'" % (time, valve_set, 'valve_setpoint')
        cursor.execute(sql)
        sql = "UPDATE fcu_valve_control SET time=%d, value=%.1f WHERE name='%s'" % (time, pQ, 'pre_Q')
        cursor.execute(sql)
    else:
        sql = "INSERT INTO fcu_control(time, id ,name, value) VALUES (%d, '%s', '%s', %.1f)" % \
              (time, '0x00000411', 'FCU_onoff_setpoint', onoff)
        cursor.execute(sql)
        sql = "INSERT INTO fcu_control(time, id ,name, value) VALUES (%d, '%s', '%s', %.1f)" % \
              (time, '0x00000413', 'FCU_fan_setpoint', fan_set)
        cursor.execute(sql)
        sql = "INSERT INTO fcu_control(time, id ,name, value) VALUES (%d, '%s', '%s', %.1f)" % \
              (time, '0x00000419', 'FCU_workingmode_setpoint', mode)
        cursor.execute(sql)
        sql = "INSERT INTO fcu_valve_control(time, id ,name, value) VALUES (%d, '%s', '%s', %.1f)" % \
              (time, '0x00000425', 'valve_setpoint', valve_set)
        cursor.execute(sql)
        sql = "INSERT INTO fcu_valve_control(time, id ,name, value) VALUES (%d, '%s', '%s', %.1f)" % \
              (time, '0x00000426', 'pre_Q', pQ)
        cursor.execute(sql)


def taskFunction(self,id,adjDirection,datalist,tasknum):
    type = datalist["type"]
    if type == 1:    
        self.sendUDP("房间开始控制",tasknum)
        db = pymysql.connect(host="localhost", user="root", passwd="cfins", db="data", charset='utf8')  # Local IP:183.173.139.213
        cursor = db.cursor()
        # set time
        sql = "SELECT %s, %s, %s, %s FROM sensor_room" % ('time', 'id', 'name', 'value')
        cursor.execute(sql)
        data1 = cursor.fetchall()
        step_min = int(data1[0][0])
        step_rec = step_min
        T_con = 15                       # 控制间隔, min
        T_delta = 10
        occ_list_length = 5              # 人数历史数据列表长度
        con_start_time = time.time()
        occ_start_time = time.time()
        H = 3
        M = 2
        L = 1
        Off = 0
        position_s = L
        position_k = L

        while(1):
            self.sendUDP('room control time: %d min' % step_min,tasknum)
            con_start_time = time.time()
            if (step_min - step_rec) % T_con == 0:
                tem_s, tem_k, position_k = R_room_node(db)
                position_s = cal_fcu_fan(tem_s, tem_k, position_k)
            temp_list, f_list, tws_list, twr_list = R_room_his(db, 10, step_min)     # length should be an even number
            pQ,Qw2 = pre_Q(temp_list, f_list, tws_list, twr_list, position_s, tem_s)
            # self.sendUDP(str(pQ)+"  "+str(Qw2),tasknum)
            W_room_node_control(db, step_min, 1, position_s, 2, 100, pQ)
            db.commit()
            step_min += 1

            if T_delta + con_start_time - time.time() > 0:
                time.sleep(T_delta + con_start_time - time.time())
        db.close()
    else:
        T_delta = 10
        while(1):
            time.sleep(T_delta)       
    return 0