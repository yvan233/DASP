# 模拟节点故障，并在节点重启后重连进系统
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

# kill room_2
nodenumber = 2
nodelist[nodenumber-1].kill()

# 等待系统函数扫描到room_2断开，实际上检测到断开后需要30*10s才会彻底断开连接
time.sleep(120)

# 重新启动room_2节点进程
node = Node(nodenumber)
nodelist[nodenumber-1] = node
print("启动room_2")
