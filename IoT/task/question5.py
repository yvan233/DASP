import time
import pymysql

# 计算末端总负荷需求 (kJ/min)
def cal_Q(db):
    cursor = db.cursor()
    sql = "SELECT %s, %s, %s, %s FROM fcu_panel" % ('time', 'id', 'name', 'value')
    cursor.execute(sql)
    data = cursor.fetchall()
    for i in range(0, 6):
        if data[i][2] == 'room_Q':
            Q = float(data[i][3])
    return Q


# 计算水泵供回水温差 (单位)
def cal_deltaT(db):
    cursor = db.cursor()
    sql = "SELECT %s, %s, %s, %s FROM sensor_temp " % ('time', 'id', 'name', 'value')
    cursor.execute(sql)
    data = cursor.fetchall()
    if data:
        for i in range(0, 2):
            if data[i][2] == 'pump_supplytemp':
                tem_supply = float(data[i][3])
            if data[i][2] == 'pump_returntemp':
                tem_return = float(data[i][3])
        deltaT = tem_supply - tem_return
    else:
        deltaT = 5.0
    return deltaT


# 读取水泵流量 和 频率(单位)
def read_pump(db):
    cursor = db.cursor()
    sql = "SELECT %s, %s, %s, %s FROM pump_vfd" % ('time', 'id', 'name', 'value')
    cursor.execute(sql)
    data = cursor.fetchall()
    speed = float(data[0][3])

    sql = "SELECT %s, %s, %s, %s FROM sensor_pumpflow" % ('time', 'id', 'name', 'value')
    cursor.execute(sql)
    data = cursor.fetchall()
    G_k = float(data[0][3])

    return G_k,speed

def judge(G_s,G_k):
    a1 = 1.0
    a2 = 2.0
    a3 = 3.0

    s2 = 2.0
    s1 = 1.0
    s0 = 0.0

    deltaSpeed = 0.0
    delta = G_s -G_k
    if delta > a3 :
        deltaSpeed = s2
    elif  a2 < delta <= a3:
        deltaSpeed = s2
    if a1 <delta <= a2:
        deltaSpeed = s1
    elif  -a1 < delta <= a1:
        deltaSpeed = s0
    elif  -a2 < delta <= -a1:
        deltaSpeed = -s1
    elif  -a3 < delta <= -a2:
        deltaSpeed = -s2
    elif  delta <= -a3:
        deltaSpeed = -s2
    return deltaSpeed

# 控制水泵频率 (Hz)
def con_pump(G_s,G_k,speed_k,deltaSpeed_last):
    speed_s = 25
    speed_lower = 25
    speed_upper = 50
    a1 = 1.0
    a2 = 2.0
    a3 = 3.0

    s2 = 2.0
    s1 = 1.0
    s0 = 0.0
    s = 0.0
    if G_s - G_k >= a3:
        s = s2
    elif a2 < G_s - G_k <= a3 and deltaSpeed_last == s2:
        s = s2
    elif a2 <= G_s - G_k < a3 and deltaSpeed_last == s1:
        s = s1
    elif a2 <= G_s - G_k < a3 and deltaSpeed_last == s0:
        s = s1
    elif a1 < G_s - G_k <= a2 and deltaSpeed_last == s1:
        s = s1
    elif a1 <= G_s - G_k < a2 and deltaSpeed_last == s0:
        s = s0
    elif a1 <= G_s - G_k < a2 and deltaSpeed_last == s2:
        s = s1
    elif -a1 <= G_s - G_k <= a1:
        s = s0
    elif -a2 <= G_s - G_k < -a1 and deltaSpeed_last == -s0:
        s = s0
    elif -a2 <= G_s - G_k < -a1 and deltaSpeed_last == -s1:
        s = -s1
    elif -a2 <= G_s - G_k < -a1 and deltaSpeed_last == -s2:
        s = -s1
    elif -a3 <= G_s - G_k < -a2 and deltaSpeed_last == -s1:
        s = -s1
    elif -a3 <= G_s - G_k < -a2 and deltaSpeed_last == -s2:
        s = -s2
    elif -a3 <= G_s - G_k < -a2 and deltaSpeed_last == -s0:
        s = -s1
    elif  G_s - G_k < -a3:
        s = -s2
    speed_s = speed_k + s
    deltaSpeed_last_n = s
     # 输出限幅
    if speed_s < speed_lower:
        speed_s = 25
    if speed_s > speed_upper:
        speed_s = 50
    return speed_s, deltaSpeed_last_n

# 写水泵控制表
def write_controlpump(db, time, speed_s):
    cursor = db.cursor()
    sql = "INSERT INTO pump_vfd_control_his(time, id ,name, value) VALUES (%d, '%s', '%s', %.1f)" % \
          (time, '0x24000208', 'pump_onoff_setpoint', 1)
    cursor.execute(sql)
    sql = "INSERT INTO pump_vfd_control_his(time, id ,name, value) VALUES (%d, '%s', '%s', %.1f)" % \
          (time, '0x24000216', 'pump_frequency_setpoint', speed_s)
    cursor.execute(sql)
    sql = "INSERT INTO pump_valve_control_his(time, id ,name, value) VALUES (%d, '%s', '%s', %.1f)" % \
          (time, '0x24000243', 'pump_valve_setpoint', 1)
    cursor.execute(sql)
    sql = "SELECT %s, %s, %s, %s FROM pump_vfd_control" % ('time', 'id', 'name', 'value')
    cursor.execute(sql)
    data = cursor.fetchall()
    if data:
        sql = "UPDATE pump_vfd_control SET time=%d, value=%.1f WHERE name='%s'" % (time, 1, 'pump_onoff_setpoint')
        cursor.execute(sql)
        sql = "UPDATE pump_vfd_control SET time=%d, value=%.1f WHERE name='%s'" % (time, speed_s, 'pump_frequency_setpoint')
        cursor.execute(sql)
        sql = "UPDATE pump_valve_control SET time=%d, value=%.1f WHERE name='%s'" % (time, 1, 'pump_valve_setpoint')
        cursor.execute(sql)
    else:
        sql = "INSERT INTO pump_vfd_control(time, id ,name, value) VALUES (%d, '%s', '%s', %.1f)" % \
              (time, '0x24000208', 'pump_onoff_setpoint', 1)
        cursor.execute(sql)
        sql = "INSERT INTO pump_vfd_control(time, id ,name, value) VALUES (%d, '%s', '%s', %.1f)" % \
              (time, '0x24000216', 'pump_frequency_setpoint', speed_s)
        cursor.execute(sql)
        sql = "INSERT INTO pump_valve_control(time, id ,name, value) VALUES (%d, '%s', '%s', %.1f)" % \
              (time, '0x24000243', 'pump_valve_setpoint', 1)
        cursor.execute(sql)

def taskFunction(self,id,adjDirection,datalist,tasknum):
    db = pymysql.connect(host="localhost", user="root", passwd="cfins", db="data", charset='utf8')
    cursor = db.cursor()
    type = datalist["type"]

    
    if type == 2:  #pump_1
        T_delta = 10
        T_inter_Q = 30
        T_inter_con = 5
        speed_s = 25.0
        G_s = 0
        Qtotal = 0
        deltaT = cal_deltaT(db)
        G_s = Qtotal / (4.2 * 1000 * deltaT) * 60     # m3/h
        start_time_Q = time.time()

        deltaSpeed_last = 0
        start_time_con = time.time()
        sql = "SELECT %s, %s, %s, %s FROM sensor_temp " % ('time', 'id', 'name', 'value')
        cursor.execute(sql)
        data = cursor.fetchall()
        step_min = int(data[0][0])
        step_rec = step_min
        while (1):
            start_time = time.time()
            print('pump control time: %d min' % step_min)
            if (step_min - step_rec) % T_inter_Q == 0:
                ## 计算总负荷
                Q = 0
                sonDirection = self.sonDirection[tasknum]
                parentDirection = self.parentDirection[tasknum]
                sonFlag = []
                sonPeopleData = []
                for ele in sonDirection:
                    sonFlag.append(0)
                    sonPeopleData.append([])
                if parentDirection == 0:
                    Qtotal = 0
                if sonDirection == []:
                    self.sendDataToDirection(parentDirection, [Q],tasknum)
                else:
                    while 1:
                        time.sleep(0.1)
                        for i in range(len(sonDirection)):
                            for j in range(len(adjDirection)):
                                if (sonDirection[i] == adjDirection[j]):
                                    if self.adjData[tasknum][j] != []:
                                        sonFlag[i] = 1
                                        sonPeopleData[i] = self.adjData[tasknum][j][0]
                        tmp = 1
                        if 0 in sonFlag:
                            tmp = 0
                        if tmp == 1:
                            break
                    sonQ = sum(sonPeopleData)
                    for i in range(len(sonDirection)):
                        sonFlag[i] = 0
                    if parentDirection != 0:
                        self.sendDataToDirection(parentDirection, [sonQ + Q],tasknum)
                    else:
                        Qtotal = sonQ + Q
                        self.sendUDP("末端总负荷需求："+str(Qtotal),tasknum)
            step_min += 1
            if T_delta + start_time - time.time() > 0:
                time.sleep(T_delta + start_time - time.time())
    else:
        T_delta = 10
        T_inter_Q = 30
        step_min = 0
        step_rec = step_min
        while (1):
            start_time = time.time()
            
            if (step_min - step_rec) % T_inter_Q == 0:
                ## 计算总负荷
                if type == 1:
                    Q = cal_Q(db)
                    self.sendUDP("Q:"+str(Q),tasknum)
                else:
                    Q = 0
                sonDirection = self.sonDirection[tasknum]
                parentDirection = self.parentDirection[tasknum]
                sonFlag = []
                sonPeopleData = []
                for ele in sonDirection:
                    sonFlag.append(0)
                    sonPeopleData.append([])
                if parentDirection == 0:
                    Qtotal = 0
                if sonDirection == []:
                    self.sendDataToDirection(parentDirection, [Q],tasknum)
                else:
                    while 1:
                        time.sleep(0.1)
                        for i in range(len(sonDirection)):
                            for j in range(len(adjDirection)):
                                if (sonDirection[i] == adjDirection[j]):
                                    if self.adjData[tasknum][j] != []:
                                        sonFlag[i] = 1
                                        sonPeopleData[i] = self.adjData[tasknum][j][0]
                        tmp = 1
                        if 0 in sonFlag:
                            tmp = 0
                        if tmp == 1:
                            break
                    sonQ = sum(sonPeopleData)
                    for i in range(len(sonDirection)):
                        sonFlag[i] = 0
                    if parentDirection != 0:
                        self.sendDataToDirection(parentDirection, [sonQ + Q],tasknum)
                    else:
                        Qtotal = sonQ + Q
                        self.sendUDP("末端总负荷需求："+str(Qtotal),tasknum)
            step_min += 1
            if T_delta + start_time - time.time() > 0:
                time.sleep(T_delta + start_time - time.time())
    db.close()
    return 1





    