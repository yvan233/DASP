# 测试任务的暂停和恢复功能
# 另外需要运行./script_PC/moniter.py   
# 可以修改./DASP/task_info/testpause/question中timesleep的形式，比较差异
import time 
import sys
sys.path.insert(1,".") 
from DASP.module import Node
from DASP.control import ControlMixin

nodelist = []
Controlmixin = ControlMixin("Pc")
nodeNum = 12  # 节点数量
rootnode = "room_1"

for i in range(nodeNum):
    node = Node(i+1)
    nodelist.append(node)

print("启动系统")
Controlmixin.RunSystem(rootnode)
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