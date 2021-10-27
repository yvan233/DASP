# 计算风机盘管挡位
def cal_fcu_fan_heating(tem_s, tem_k, position_k, onoff_requriment):
    H = 1
    M = 2
    L = 3
    Off = 0
    a1 = 0.5
    a2 = 1
    a3 = 2
    a4 = 3
    position_s = 0
    if onoff_requriment == 1:
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
    else:
        position_s = 0
    return position_s

def cal_fcu_fan_cooling(tem_s, tem_k, position_k, onoff_requriment):
    H = 1
    M = 2
    L = 3
    Off = 0
    a1 = 0.5
    a2 = 1
    a3 = 2
    a4 = 3
    
    if onoff_requriment == 1:
        if tem_k - tem_s > a4:
            position_s = H
        elif a3 <= tem_k - tem_s < a4 and (position_k == M):
            position_s = M
        elif a3 < tem_k - tem_s <= a4 and (position_k == H):
            position_s = H
        elif a3 < tem_k - tem_s <= a4 and (position_k == L):
            position_s = M
        elif a2 < tem_k - tem_s <= a3:
            position_s = M
        elif a1 <= tem_k - tem_s < a2 and (position_k == L):
            position_s = L
        elif a1 < tem_k - tem_s <= a2 and (position_k == M):
            position_s = M
        elif a1 < tem_k - tem_s <= a2 and (position_k == H):
            position_s = M
        elif -a2 < tem_k - tem_s <= a1:
            position_s = L
        # elif -a4 <tem_s - tem_k <= -a2 and (position_k == L):
        #     position_s = L
        elif -a4 < tem_k - tem_s <= -a2 and (position_k == L or position_k == M or position_k == H):
            position_s = L
        elif -a4 < tem_k - tem_s <= -a2 and (position_k == Off):
            position_s = Off
        elif -a4 < tem_k - tem_s <= -a2 and (position_k == Off):
            position_s = Off
        elif tem_k - tem_s <= -a4:
            position_s = Off
    else:
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
            k = (Qw1 - Qw2) / 0.2 * sign(dt1 - dt2)
        pQ = Qw2 + math.exp(-1) * k * (dt_demand - dt2)
    else:
        pQ = Qw2
    return pQ


# Alarming
def alarming(db, time, tem_s, tem_k):
    cursor = db.cursor()
    if math.abs(tem_s - tem_k) > 4:
        temp_alarm = 1
    else:
        temp_alarm = 0

    data1 = db_read(cursor, 'sensor_fcu_waterflow', 'waterflow', 0)
    if data1:
        fcu_flow = float(data1[0][3])
    else:
        fcu_flow = 0
    data2 = db_read(cursor, 'fcu_panel', 'FCU_onoff_feedback', 0)
    if data2:
        fcu_onoff = float(data2[0][3])
    else:
        fcu_onoff = 0
    if fcu_onoff > 0 and fcu_flow < 0.2:
        fcuflow_alarm = 1
    else:
        fcuflow_alarm = 0

    sql = "SELECT %s, %s, %s, %s FROM sensor_fcu_watertemp" % ('time', 'id', 'name', 'value')
    cursor.execute(sql)
    data3 = cursor.fetchall()
    if data3:
        tw_sup = float(data3[0][3])
        tw_return = float(data3[1][3])
    else:
        tw_sup = 10
        tw_return = 10
    if tw_sup < 5 or tw_return < 5:
        tw_alarm = 1
    else:
        tw_alarm = 0

    # write alarms
    db_insert(cursor, 'alarm_his', time, '0x00000900', 'room_temp_alarm', temp_alarm)
    db_insert(cursor, 'alarm_his', time, '0x00000903', 'fcu_flow_alarm', fcuflow_alarm)
    db_insert(cursor, 'alarm_his', time, '0x00000904', 'fcu_tw_alarm', tw_alarm)
    sql = "SELECT %s, %s, %s, %s FROM alarm" % ('time', 'id', 'name', 'value')
    cursor.execute(sql)
    data = cursor.fetchall()
    if data:
        db_update(cursor, 'alarm', time, 'room_temp_alarm', temp_alarm)
        db_update(cursor, 'alarm', time, 'fcu_flow_alarm', fcuflow_alarm)
        db_update(cursor, 'alarm', time, 'fcu_tw_alarm', tw_alarm)
    else:
        db_insert(cursor, 'alarm', time, '0x00000900', 'room_temp_alarm', temp_alarm)
        db_insert(cursor, 'alarm', time, '0x00000903', 'fcu_flow_alarm', fcuflow_alarm)
        db_insert(cursor, 'alarm', time, '0x00000904', 'fcu_tw_alarm', tw_alarm)
