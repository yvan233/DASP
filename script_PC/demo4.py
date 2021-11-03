# 测试节点一个个启动，逐步接入网络
# 需要把./DASP/task_info/system/question的time改为10s，方便查看
# 另外需要运行./script_PC/moniter.py
import time 
import sys
sys.path.insert(1,".") 
from DASP.module import Node
from DASP.control import ControlMixin

nodelist = []
Controlmixin = ControlMixin
node = Node(1)
nodelist.append(node)

print("启动系统")
# Controlmixin.RunSystem("room_1")


time.sleep(30)
node = Node(2)
nodelist.append(node)
print("启动room_2")
# Controlmixin.reconnect("room_2")

time.sleep(15)
node = Node(3)
nodelist.append(node)
print("启动room_3")
# Controlmixin.reconnect("room_3")


"""
[room_1]system: 接收任务请求
[room_1]system: 与邻居节点room_2连接失败
[room_1]system: 与邻居节点room_4连接失败
[room_1]system: 通信树建立完成
[room_1]system: 开始执行
[room_1]system: 系统第1次自检：本节点与所有邻居通信正常，当前邻居节点：[]
[room_1]system: 系统第2次自检：本节点与所有邻居通信正常，当前邻居节点：[]
[room_2]system: 重新连入系统
[room_1]system: 与邻居节点room_2重连成功，已添加和room_2的连接
[room_2]system: 与邻居节点room_3连接失败
[room_2]system: 与邻居节点room_5连接失败
[room_2]system: 开始执行
[room_2]system: 系统第1次自检：本节点与所有邻居通信正常，当前邻居节点：['room_1']
[room_1]system: 系统第3次自检：本节点与所有邻居通信正常，当前邻居节点：['room_2']
[room_2]system: 系统第2次自检：本节点与所有邻居通信正常，当前邻居节点：['room_1']
[room_3]system: 重新连入系统
[room_2]system: 与邻居节点room_3重连成功，已添加和room_3的连接
[room_3]system: 与邻居节点room_6连接失败
[room_1]system: 系统第4次自检：本节点与所有邻居通信正常，当前邻居节点：['room_2']
[room_3]system: 与邻居节点pump_1连接失败
[room_3]system: 开始执行
[room_3]system: 系统第1次自检：本节点与所有邻居通信正常，当前邻居节点：['room_2']
[room_2]system: 系统第3次自检：本节点与所有邻居通信正常，当前邻居节点：['room_1', 'room_3'] 
"""