# 测试任务的暂停和恢复功能
# 可以修改./DASP/task_info/testpause/question中timesleep的形式，比较差异
import time 
import sys
sys.path.insert(1,".") 
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

for i in range(nodeNum):
    node = Node(i)
    nodelist.append(node)

time.sleep(2)

DAPPname = "testpause"
print("开始任务")
Controlmixin.StartTask(DAPPname,rootnode)

time.sleep(5)
print("发送pause信号")
Controlmixin.PauseTask(DAPPname,rootnode)

time.sleep(5)
print("发送resume信号")
Controlmixin.ResumeTask(DAPPname,rootnode)

time.sleep(5)
print("发送终止信号")
Controlmixin.StopTask(DAPPname,rootnode)