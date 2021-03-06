# 启动系统并运行分布式算法
# 另外需要运行./script_PC/moniter.py

import time 
import sys
sys.path.insert(1,".") # 把上一级目录加入搜索路径
from DASP.module import Node
from DASP.control import ControlMixin

nodeNum = 12  # 节点数量
rootnode = "room_1" # 根节点ID
nodelist = [] # 节点进程列表
Controlmixin = ControlMixin("Pc") # 控制函数集合

# 启动节点进程
for i in range(nodeNum):
    node = Node(i+1)
    nodelist.append(node)

time.sleep(2)
DAPPname = "CreateBFStree"
print("开始任务："+DAPPname)
Controlmixin.StartTask(DAPPname,rootnode)