# 并行示例
import time 
import sys
sys.path.insert(1,".") # 把上一级目录加入搜索路径
from threading import Thread
from DASP.module import Node,moniter
from DASP.control import ControlMixin

nodeNum = 9  # 节点数量
rootnode = "room_1" # 根节点ID
nodelist = [] # 节点进程列表
Controlmixin = ControlMixin("Pc") # 控制函数集合

# 启动监控脚本
t = Thread(target=moniter,)    
t.start()

# 启动节点进程
for i in range(nodeNum):
    node = Node(i)
    nodelist.append(node)

time.sleep(2)

DAPPname = "BFStree"
print("开始任务："+DAPPname)
Controlmixin.StartTask(DAPPname,rootnode)

# 并行示例
time.sleep(1)
DAPPname = "ALST"
print("开始任务："+DAPPname)
Controlmixin.StartTask(DAPPname,rootnode)