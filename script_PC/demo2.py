# 并行示例
import time 
import sys
sys.path.insert(1,".") # 把上一级目录加入搜索路径
from DASP.module import Node,Moniter
from DASP.control import ControlMixin

nodeNum = 9  # 节点数量
rootnode = "room_1" # 根节点ID
nodelist = [] # 节点进程列表
controlMixin = ControlMixin("Pc") # 控制函数集合

# 启动监控脚本
moniter = Moniter()
moniter.run()

# 启动节点进程
for i in range(nodeNum):
    node = Node(i)
    nodelist.append(node)

time.sleep(2)

DappName = "BFStree"
print("开始任务："+DappName)
controlMixin.startTask(DappName,rootnode)

# 并行示例
time.sleep(1)
DappName = "ALST"
print("开始任务："+DappName)
controlMixin.startTask(DappName,rootnode)

moniter.wait()