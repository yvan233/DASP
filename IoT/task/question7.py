import copy
import time
import socket
import json
import pymysql

def sendDataToServer(IP,PORT,data):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (IP, PORT)
    s.sendto(json.dumps(data).encode(), addr)
    response, addr = s.recvfrom(1024)
    print(response.decode())
    s.close()
    
def get_numberpeople():
    db = pymysql.connect(host='localhost', port=3306,user="root", passwd="cfins", db="data",charset='utf8')
    cursor = db.cursor()
    sql='select * from sensor_camera_numberpeople where time = (select max(time) from sensor_camera_numberpeople);'
    cursor.execute(sql)
    info = cursor.fetchall()
    db.commit() 
    cursor.close()
    db.close()
    return [info[0][0],int(info[0][-1])]

def get_temperature():
    db = pymysql.connect(host='localhost', port=3306,user="root", passwd="cfins", db="data",charset='utf8')
    cursor = db.cursor()
    sql='select * from sensor_temperature where time = (select max(time) from sensor_temperature);'
    cursor.execute(sql)
    info = cursor.fetchall()
    db.commit() 
    cursor.close()
    db.close()
    return [info[0][0],info[0][-1]]

def get_sensor_fan():
    result = []
    db = pymysql.connect(host='localhost', port=3306,user="root", passwd="cfins", db="data",charset='utf8')
    cursor = db.cursor()
    id = "0x00003023"
    sql='select * from sensor_fan where id = "%s" and time = (select max(time) from sensor_fan where id = "%s");' % (id,id)
    cursor.execute(sql)
    info = cursor.fetchall()
    db.commit() 
    result.append([info[0][0],info[0][-1]])

    id = "0x00003025"
    sql='select * from sensor_fan where id = "%s" and time = (select max(time) from sensor_fan where id = "%s");' % (id,id)
    cursor.execute(sql)
    info = cursor.fetchall()
    db.commit() 
    result.append([info[0][0],info[0][-1]])

    id = "0x00003040"
    sql='select * from sensor_fan where id = "%s" and time = (select max(time) from sensor_fan where id = "%s");' % (id,id)
    cursor.execute(sql)
    info = cursor.fetchall()
    db.commit() 
    result.append([info[0][0],info[0][-1]])

    id = "0x00003079"
    sql='select * from sensor_fan where id = "%s" and time = (select max(time) from sensor_fan where id = "%s");' % (id,id)
    cursor.execute(sql)
    info = cursor.fetchall()
    db.commit() 
    result.append([info[0][0],info[0][-1]])

    cursor.close()
    db.close()
    return result

def get_controller_fan():
    result = []
    db = pymysql.connect(host='localhost', port=3306,user="root", passwd="cfins", db="data",charset='utf8')
    cursor = db.cursor()
    id = "0x00003022"
    sql='select * from controller_fan where id = "%s" and time = (select max(time) from controller_fan where id = "%s");' % (id,id)
    cursor.execute(sql)
    info = cursor.fetchall()
    db.commit() 
    result.append([info[0][0],info[0][-1]])

    id = "0x00003024"
    sql='select * from controller_fan where id = "%s" and time = (select max(time) from controller_fan where id = "%s");' % (id,id)
    cursor.execute(sql)
    info = cursor.fetchall()
    db.commit() 
    result.append([info[0][0],info[0][-1]])

    cursor.close()
    db.close()
    return result
    
def taskFunction(self,id,adjDirection,datalist,tasknum):
    type = datalist["type"]
    IP = self.GUIinfo[0]
    PORT = 12345
    parent_direction = copy.deepcopy(self.parentDirection[tasknum])
    child_direction = copy.deepcopy(self.sonDirection[tasknum])
    
    if type == 1:
        numberpeople = [1,2]
        temper =[1,20]
        J = [
            [
                id,
                {
                    "sensor_camera_numberpeople": [
                        {
                            "time" : numberpeople[0],
                            "id" : "0x12632102",
                            "name": "numberpeople",
                            "value": numberpeople[1]
                        }
                    ],
                    "sensor_temperature": [
                        {
                            "time" : temper[0],
                            "id" : "0x11002101",
                            "name": "temperature",
                            "value": temper[1]
                        }
                    ]
                }
            ]
        ]
    else:
        controller_fan = [[1,2],[1,2]]
        sensor_fan = [[1,2],[1,2],[1,2],[1,2]]
        J = [
            [
                id,
                {
                    "controller_fan": [
                        {
                            "time": controller_fan[0][0],
                            "id": "0x00003022",
                            "name": "fan_onoff_set",
                            "value": controller_fan[0][1]
                        },
                        {
                            "time": controller_fan[1][0],
                            "id": "0x00003024",
                            "name": "fan_speed_set",
                            "value": controller_fan[1][1]
                        }
                    ],
                    "sensor_fan":[
                        {
                            "time": sensor_fan[0][0],
                            "id": "0x00003023",
                            "name": "fan_onoff",
                            "value": sensor_fan[0][1]
                        },
                        {
                            "time": sensor_fan[1][0],
                            "id": "0x00003025",
                            "name": "fan_speed",
                            "value": sensor_fan[1][1]
                        },
                        {
                            "time": sensor_fan[2][0],
                            "id": "0x00003040",
                            "name": "fan_power",
                            "value": sensor_fan[2][1]
                        },
                        {
                            "time": sensor_fan[3][0],
                            "id": "0x00003079",
                            "name": "fan_cost",
                            "value": sensor_fan[3][1]
                        }
                    ]
                }
            ]
        ]
    # self.sendUDP("J为："+str(J),tasknum)
    End_Counter = len(child_direction)
    # data_base = [0,False,False,J]  # 邻居方向,COMPUTE, VALUE, J
    data = []
    if parent_direction:
        data_base_temp = [parent_direction,False,False,J]  
        data.append(data_base_temp)

    if len(child_direction):
        for i in range(len(child_direction)):
            data_base_temp = [child_direction[i],False,False,J]  
            data.append(data_base_temp)

    if parent_direction == 0:
        for i in range(len(data)):
            data[i][1] = True    #COMPUTE            

    for m in range(18):
        transdata = [one[1:] for one in data]     
        tansdirection = [one[0] for one in data]                            
        adjDirection_fb,adjData_fb = self.transmitData(tansdirection, transdata, tasknum)    # 获取邻居传输的数据       
        for i in range(len(data)):
            data[i][1] = False    #COMPUTE
            data[i][2] = False    #VALUE

        for i in range(len(adjData_fb)):
            if adjData_fb[i]:
                if adjData_fb[i][0] == True:   #COMPUTE
                    if len(child_direction):
                        for k in range(len(data)):
                            if data[k][0] != adjDirection_fb[i]:
                                data[k][1] = True    #COMPUTE
                    else:
                        for k in range(len(data)):
                            if data[k][0] == adjDirection_fb[i]:
                                data[k][2] = True    #VALUE                   

                if  adjData_fb[i][1] == True:  #VALUE 

                    J = J + adjData_fb[i][2]

                    for k in range(len(data)):
                        data[k][3] = J       

                    End_Counter = End_Counter - 1
                    if End_Counter == 0:
                        for k in range(len(data)):
                            if data[k][0] == parent_direction:
                                data[k][1] = False   #COMPUTE
                                data[k][2] = True    #VALUE 

        # self.sendUDP("第" + str(m+1) + "步完成",tasknum)
    if parent_direction == 0:
        self.sendUDP("计算结果为："+str(J),tasknum)
        # sendDataToServer("192.168.3.35",PORT,J)
    return 0