# 测试多进程开启节点

import subprocess
import time
proc = subprocess.Popen(['python','./DASP/system/initial.py', '1'],\
     shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
data = []
while True:
    rcode = proc.poll()
    # 若进程未结束,没结束是None，结束了是0
    if rcode is None:
        print('[subprocess1]: ', end='')
        line = proc.stdout.readline().strip().decode()
        data.append(line)
        print(line)
    else:
        break
    time.sleep(0.01)
        