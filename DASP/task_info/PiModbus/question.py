import subprocess
import threading
import time
        
def getprintdata(proc, mprint):
    """
    获取输出数据
    """
    while True:
        rcode = proc.poll()
        # 若进程未结束
        if rcode is None:
            line = proc.stdout.readline().strip().decode('GBK')  #cmd窗口默认GBK编码
            mprint(line)
        else:
            break
        time.sleep(0.01)

def taskFunction(self, id, adjDirection, datalist):
    if id in ["room_1", "room_2", "room_3", "room_7"]:
        # -u参数是为了读取缓冲区中的打印信息
        proc = subprocess.Popen(['python3','-u','2nd_pymodbus.py', str()],\
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=r'/home/pi/xt')
    elif id in ["room_4", "room_5", "room_6"]:
        # -u参数是为了读取缓冲区中的打印信息
        proc = subprocess.Popen(['python3','-u','1st_pymodbus.py', str()],\
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=r'/home/pi/xt')
    thread = threading.Thread(target=getprintdata,args=(proc,self.sendDatatoGUI,))
    thread.start()
    thread.join()
    return 0