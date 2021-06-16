# request = "1123\r\n123\r\n334"
# form = request.split('\r\n')[-1]
# print (form)

# import os
# import codecs
# path = os.getcwd() + "\\IoT\\system\\topology.txt"
# path = path.replace('\\', '/')   
# text = codecs.open(path, 'r', 'utf-8').read()
# a = 1

import sys
sys.path.insert(1,".")  # 把上一级目录加入搜索路径
from DASP.module import TaskServer

taskserver = TaskServer("12",12)