# 测试任务的暂停和恢复功能
# 可以修改./DASP/task_info/testpause/question中timesleep的形式，比较差异
import time 
import sys
sys.path.insert(1,".") 
from DASP.module import Node,Moniter
from DASP.control import ControlMixin

nodeNum = 9  # 节点数量
startNode = "room_1" # 起始节点ID
nodelist = [] # 节点进程列表
controlMixin = ControlMixin("Pc") # 控制函数集合

# 启动监控脚本
moniter = Moniter()
moniter.run()

for i in range(nodeNum):
    node = Node(i)
    nodelist.append(node)

time.sleep(2)

DappName = "testpause"
print("开始任务")
controlMixin.startTask(DappName,startNode)

time.sleep(5)
print("发送pause信号")
controlMixin.pauseTask(DappName,startNode)

time.sleep(5)
print("发送resume信号")
controlMixin.resumeTask(DappName,startNode)

time.sleep(5)
print("发送终止信号")
controlMixin.stopTask(DappName,startNode)

moniter.wait()