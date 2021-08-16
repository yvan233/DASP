# 自动启动脚本
import json
import time
import socket
import subprocess,threading
import struct
headformat = "!2I"
headerSize = 8
def sendall_length(socket, jsondata, methods = 1):
    '''
    为发送的json数据添加methods和length报头
        POST：methods = 1: 
    '''
    body = json.dumps(jsondata)
    header = [methods, body.__len__()]
    headPack = struct.pack(headformat , *header)
    socket.sendall(headPack+body.encode())



class Proc:
    """用于多进程开启脚本   
    属性:
        path: 脚本路径
        mode: 是否直接打印输出数据
        proc: 节点进程
        thread: 节点获取输出数据线程
        
        """
        
    def __init__(self, path, mode):
        """
        mode: 是否直接打印输出数据
        """
        # -u参数是为了读取缓冲区中的打印信息
        self.proc = subprocess.Popen(['python','-u', path],\
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.thread = threading.Thread(target=self.getprintdata,args=(mode,))
        self.thread.start()
        
    def getprintdata(self, mode = False):
        """
        获取输出数据
        """
        while True:
            rcode = self.proc.poll()
            # 若进程未结束
            if rcode is None:
                line = self.proc.stdout.readline().strip().decode('GBK')  #cmd窗口默认GBK编码
                if line and mode:
                    print(line)
            else:
                break
            time.sleep(0.01)

    def kill(self):
        """
        杀死节点进程
        """
        self.proc.kill()
        self.proc.wait()
        print ("[node{}]: 进程已被杀死".format(self.num))

proc = Proc('./DASP/tdebugtemp/test.py',True)
proc = Proc('./DASP/tdebugtemp/test.py',True)
# 启动DASP
# print("启动系统")
# localIP = socket.gethostbyname(socket.gethostname())
# GUIinfo = [localIP, 50000]
# data = {
#     "key": "startsystem",
#     "GUIinfo": GUIinfo
# }
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((localIP, 10006))
# sendall_length(s, data)
# s.close()
# time.sleep(5)


# import time
# # 检测远程服务器，非空才继续
# while True:
#     time.sleep(0.1)
#     #db
    
#     if True:

#         break


# # 按顺序启动脚本





# # 启动DAPP
# DAPPnamelist = ["DA_W"]
# print("启动任务")
# for ele in DAPPnamelist:
#     localIP = socket.gethostbyname(socket.gethostname())
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.connect((localIP, 10006))
#     data = {
#         "key": "newtask",
#         "DAPPname": ele,
#     }
#     sendall_length(s, data)
#     s.close()
