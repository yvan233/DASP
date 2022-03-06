import copy
import time 
import airgym
import airsim
import gym
import numpy as np
import math
from threading import Thread

def taskFunction(self,id,adjDirection,datalist):
    type = datalist["Type"]
    # 摄像机视角
    if type == "Camera":
        for UE_name,pose in datalist["Init_pose"].items():
            data = {"Key": "Request IP"}
            self.sendDataToID(UE_name, data)
    # Car agent
    elif type == "Car":
        pass
    # UE agent
    elif type == "UE":
        pass
    else:
        pass

    self.sendDatatoGUI(f"{datalist}")

    return datalist

def list2pose(arr):
    return airsim.Pose(airsim.Vector3r(arr[0],arr[1],0),airsim.to_quaternion(0,0,arr[2]/180*math.pi))