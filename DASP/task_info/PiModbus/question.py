import subprocess
import time

def taskFunction(self, id, adjDirection, datalist):
    ScriptName = ''
    if id in ['room_1', 'room_2', 'room_3']:
        ScriptName = '2nd_run.py'
    elif id in ['room_4', 'room_5', 'room_6', 'room_7']:
        ScriptName = '1st_run.py'
    elif id in ['pump_1']:
        ScriptName = 'pump_run.py'
    elif id in ['heatpump_1']:
        ScriptName = 'heatpump_run.py'
    if ScriptName:
        # -u参数是为了读取缓冲区中的打印信息
        proc = subprocess.Popen(['python3','-u', ScriptName],\
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=r'/home/pi/xingtian')
        while True:
            returncode = proc.poll()
            # 若进程未结束
            if returncode is None:
                line = proc.stdout.readline().strip().decode()  #cmd窗口默认GBK编码
                if line:
                    self.sendDatatoGUI(line)
            else:
                break
            time.sleep(0.01)
    return 0