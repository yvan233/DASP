# 测试输出流
import subprocess
import os
import time

proc = subprocess.Popen(['python','./DASP/system/initial.py', '1'],\
        shell=True)
print(proc.pid, proc.poll())
time.sleep(10)
print(proc.pid, proc.poll())
proc.kill()
proc.wait()
print(proc.poll())
time.sleep(10)