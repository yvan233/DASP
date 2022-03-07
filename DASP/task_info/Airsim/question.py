import time 
import airgym
import airsim
import gym
import numpy as np
import math
from threading import Thread


def list2pose(arr):
    return airsim.Pose(airsim.Vector3r(arr[0],arr[1],0),airsim.to_quaternion(0,0,arr[2]/180*math.pi))

def add_car(self, j, env, pose):
    env.reset()
    env.add_car(list2pose(pose))
    data = {"Key": "OK"}
    self.sendAsynchData(j,data)

def del_car(self, j, env, UE_name):
    next_UE = "UE2" if UE_name == "UE1" else "UE1"
    data = {"Key": "OK", "next_UE":next_UE}
    self.sendAsynchData(j, data)
    env.reset()
    env.del_car()

def stop_car(self, j, env):
    data = {"Key": "END"}
    self.sendAsynchData(j, data)
    env.reset()
    env.del_car()

def taskFunction(self,id,adjDirection,datalist):
    type = datalist["Type"]
    name = datalist["Name"]
    # 摄像机视角
    if type == "Camera":
        data = {"Key": "Car Init", "Name":name}
        for ele in adjDirection:
            self.sendAsynchData(ele, data)

    # Car agent
    elif type == "Car":
        UEdict = {}  # {"Name", "Ip", "Direction"}
        data = {"Key": "Request IP", "Name":name}
        for ele in adjDirection:
            self.sendAsynchData(ele,data)
        for i in adjDirection:
            j,data = self.getAsynchData()
            UEdict[data["Name"]]= data
            UEdict[data["Name"]]["Direction"] = j

        next_UE = datalist["Init_UE"]
        data = {"Key": "Car Init", "Name":name}
        while True:
            UE_info = UEdict[next_UE]
            self.sendAsynchData(UEdict[next_UE]["Direction"],data)
            j,data = self.getAsynchData()
            if data["Key"] == "OK":
                env = gym.make("airsim-car-agemt-v0", ip = UE_info["Ip"], vehicle_name = name)   
                obs, action, done = env.reset()
                t = 0 # simmulation step 
                action.throttle = 1
                while not done: 
                    obs, rewards, done, info = env.step(action)    
                    t += 1 
                print(info)
                # 移动时提供当前位置
                data = {"Key": info, "Name":name}
                self.sendAsynchData(UEdict[next_UE]["Direction"],data)
                j,data = self.getAsynchData()
                # self.sendDatatoGUI(f"{data}")
                if data["Key"] == "OK":
                    next_UE = data["next_UE"]
                    X_position = round(obs["car"].position.x_val, 2)
                    data = {"Key": "Car Move", "Name":name, "X":X_position}
                elif data["Key"] == "END":
                    break
            else:
                self.sendDatatoGUI(f"{next_UE} break down!")
                break

    # UE agent
    elif type == "UE":
        # 重置环境
        env = gym.make("airsim-car-agemt-v0", ip = datalist["Ip"])   
        env.reset()
        env.reset_env()
        while True:
            j,data = self.getAsynchData()
            self.sendDatatoGUI(f"{data}")
            car_name = data["Name"]
            if data["Key"] == "Request IP":
                self.sendAsynchData(j,{"Name":datalist["Name"], "Ip":datalist["Ip"]})
            elif data["Key"] == "Car Init":
                env = gym.make("airsim-car-agemt-v0", init_pose = list2pose(datalist["Car_park_pose"][car_name]), 
                    ip = datalist["Ip"], vehicle_name = car_name)     
                t = Thread(target=add_car,args=(self, j, env, datalist["Car_init_pose"][car_name]),)
                t.start()
            elif data["Key"] == "Car Move":
                env = gym.make("airsim-car-agemt-v0", init_pose = list2pose(datalist["Car_park_pose"][car_name]), 
                    ip = datalist["Ip"], vehicle_name = car_name)   
                # 计算转移的位置
                move_pose = [-10-data["X"]]+datalist["Move_pose_Y"]
                t = Thread(target=add_car,args=(self, j, env, move_pose),)
                t.start()
            elif data["Key"] == "go to the next section":
                env = gym.make("airsim-car-agemt-v0", init_pose = list2pose(datalist["Car_park_pose"][car_name]), 
                    ip = datalist["Ip"], vehicle_name = car_name)   
                t = Thread(target=del_car,args=(self, j, env, datalist["Name"]),)
                t.start()
            elif data["Key"] == "out of the test zone":
                env = gym.make("airsim-car-agemt-v0", init_pose = list2pose(datalist["Car_park_pose"][car_name]), 
                    ip = datalist["Ip"], vehicle_name = car_name)   
                t = Thread(target=stop_car,args=(self, j, env),)
                t.start()
    else:
        pass
    return 0

"""
[UE1]Airsim: {'Key': 'Car Init', 'Name': 'Car0'}
[UE2]Airsim: {'Key': 'Car Init', 'Name': 'Car0'}
[UE1]Airsim: {'Key': 'Request IP', 'Name': 'Car1'}   
[UE1]Airsim: {'Key': 'Request IP', 'Name': 'Escaper'}
[UE1]Airsim: {'Key': 'Request IP', 'Name': 'Catcher'}
[UE2]Airsim: {'Key': 'Request IP', 'Name': 'Car1'}
[UE2]Airsim: {'Key': 'Request IP', 'Name': 'Escaper'}
[UE2]Airsim: {'Key': 'Request IP', 'Name': 'Catcher'}
[UE2]Airsim: {'Key': 'Car Init', 'Name': 'Catcher'}
[UE1]Airsim: {'Key': 'Car Init', 'Name': 'Car1'}
[UE1]Airsim: {'Key': 'Car Init', 'Name': 'Escaper'}
[UE1]Airsim: {'Key': 'go to the next section', 'Name': 'Car1'}
[UE2]Airsim: {'Key': 'Car Move', 'Name': 'Car1', 'X': -50.02}
[UE2]Airsim: {'Key': 'go to the next section', 'Name': 'Catcher'}
[UE1]Airsim: {'Key': 'go to the next section', 'Name': 'Escaper'}
[UE1]Airsim: {'Key': 'Car Move', 'Name': 'Catcher', 'X': 19.96}
[UE2]Airsim: {'Key': 'Car Move', 'Name': 'Escaper', 'X': -40.05}
[UE2]Airsim: {'Key': 'out of the test zone', 'Name': 'Car1'}
[Car1]Airsim: 执行完毕
[UE1]Airsim: {'Key': 'out of the test zone', 'Name': 'Catcher'}
[Car3]Airsim: 执行完毕
[UE2]Airsim: {'Key': 'out of the test zone', 'Name': 'Escaper'}
[Car2]Airsim: 执行完毕
"""