# 测试subprocess对脚本报错信息的获取与打印
import subprocess
import time

proc = subprocess.Popen(['python','-u','./DASP/tdebugtemp/subproc.py', str()],\
    shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

while True:
    returncode  = proc.poll()
    # 若进程未结束
    if returncode is None:
        line = proc.stdout.readline().strip().decode()  #cmd窗口默认GBK编码
        if line:
           print(line)
    else:
        break
    time.sleep(0.01)