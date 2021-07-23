import json
import ctypes
import inspect
import struct
import platform
import socket

class DaspCommon():
    '''
    Dasp公共变量及函数


    属性:
        nodeID: 节点ID
        IP: 节点IP
        PORT: 节点端口列表
        adjID: 邻居ID
        adjDirection: 邻居方向
        adjDirectionOtherSide: 节点在邻居的方向
        adjsocket: 邻居通信套接字
        IPlist: 邻居IP及端口列表
        GUIinfo: UI界面IP及端口
        self.headformat: 自定义消息头格式，methods+length，2个无符号整形变量
        self.headerSize：自定义消息头长度，8个字节
        (包括读取拓扑文件的信息，以及所有类共有的信息)
    '''
    ### 类变量，直接通过DaspCommon.维护
    nodeID = ""
    IP = ""
    PORT = []
    adjID = []
    adjDirection = []
    adjDirectionOtherSide = []
    adjSocket = {}
    IPlist = []
    GUIinfo = ["localhost",0]    
    headformat = "!2I"
    headerSize = 8

    def __init__(self):
        pass

    def sendall_length(self, socket, jsondata, methods = 1):
        '''
        为发送的json数据添加methods和length报头
            POST: methods = 1
            REFUSE: methods = 9
        '''
        body = json.dumps(jsondata)
        header = [methods, body.__len__()]
        headPack = struct.pack(self.headformat , *header)
        socket.sendall(headPack+body.encode())

    def recv_length(self, conn):
        '''
        循环接收数据，直到收完报头中length长度的数据
            return headPack,body
        '''
        dataBuffer = bytes()
        while True:
            data = conn.recv(1024)
            # if data == b"":
            #     break
            if data:
                dataBuffer += data
                while True:
                    if len(dataBuffer) < self.headerSize:
                        break  #数据包小于消息头部长度，跳出小循环
                    # 读取包头
                    headPack = struct.unpack(self.headformat, dataBuffer[:self.headerSize])
                    bodySize = headPack[1]
                    if len(dataBuffer) < self.headerSize+bodySize :
                        break  #数据包不完整，跳出小循环
                    body = dataBuffer[self.headerSize:self.headerSize+bodySize]
                    body = body.decode()
                    body = json.loads(body)
                    return headPack,body

    def set_keep_alive(self, sock):
        """
        设置套接字保活机制
        30s后没反应开始探测连接，30s探测一次，一共探测10次，失败则断开
        """
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        if platform.system() == "Windows":
            sock.ioctl(socket.SIO_KEEPALIVE_VALS,(1,30*1000,30*1000))

        if platform.system() == "Linux":
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 10)

    def sendtoGUIbase(self, info, key, DAPPname):
        """
        通过UDP的形式将信息发送至GUI
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            addr = (DaspCommon.GUIinfo[0], DaspCommon.GUIinfo[1])
            data = {
                "key": key,
                "id": DaspCommon.nodeID,
                "DAPPname":DAPPname,
                "info": info
            }
            sock.sendto(json.dumps(data).encode('utf-8'), addr)
            sock.close()
        except Exception as e:
            print ("Failed to send" + info)

    def deleteadjID(self, id):  
        """
        删除本节点和指定id邻居节点的所有连接(DaspCommon类变量)
        """
        
        if id in DaspCommon.adjID:
            index = DaspCommon.adjID.index(id)      
            del DaspCommon.adjID[index]
            del DaspCommon.adjDirection[index]
        if id in DaspCommon.adjSocket:
            del DaspCommon.adjSocket[id]
        for ele in DaspCommon.IPlist:
            if ele != []:
                if ele[4] == id:
                    DaspCommon.IPlist.remove(ele)

    def _async_raise(self, tid, exctype):
        '''
        主动抛出异常
        '''
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop_thread(self, thread):
        '''
        强制停止某个线程
        '''
        self._async_raise(thread.ident, SystemExit)