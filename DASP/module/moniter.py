import socket
import json
import time
import threading

class Moniter:
    def __init__(self, port = 50000):
        self.port = port

    def run(self):
        t = threading.Thread(target=self.moniter,)    
        t.setDaemon(True)
        t.start()

    def moniter(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        localIP = socket.gethostbyname(socket.gethostname())
        s.bind((localIP, self.port))
        print ("moniter: {}:{}".format(localIP,self.port))
        while 1:
            try:
                data, addr = s.recvfrom(100000000)
                jdata = json.loads(data)
            except Exception:
                print ("接收数据出错")
            else:
                if jdata["key"] == "RunData":
                    print("[{}]{}: {}".format(jdata["id"], jdata["DAPPname"], jdata["info"]))
                elif jdata["key"] == "EndData":
                    print("[{}]{}运行结束，运行结果:\n{}".format(jdata["id"], jdata["DAPPname"], jdata["info"]))
                elif jdata["key"] == "RunFlag":
                    # print(str(jdata["tasknum"]) +str(jdata["info"]))
                    pass
                else:
                    print ("数据有误")

    def wait(self):
        while True:
            time.sleep(1)

if __name__ == '__main__':
    moniter = Moniter()
    moniter.run()
    moniter.wait()