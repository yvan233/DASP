# import os
# import codecs
# path = os.getcwd() + "\\IoT\\system\\topology.txt"
# path = path.replace('\\', '/')   
# text = codecs.open(path, 'r', 'utf-8').read()
# a = 1

import sys
sys.path.insert(1,".")  # 把上一级目录加入搜索路径
from IoT.server import TaskServer

taskserver = TaskServer("12",12)