# 启动系统并运行分布式算法
# 另外需要运行./script_PC/moniter.py

import time 
import sys
sys.path.insert(1,".") # 把上一级目录加入搜索路径
from DASP.control import ControlMixin

rootnode = "room_1" # 根节点ID
Controlmixin = ControlMixin("PI") # 控制函数集合


print("启动系统")
Controlmixin.RunSystem(rootnode)
time.sleep(2)