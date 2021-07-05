import socket
import json
import ctypes
import inspect

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
        IPlist: 邻居IP及端口列表
        GUIinfo: UI界面IP及端口
        (包括读取拓扑文件的信息，以及所有类共有的信息)
    '''
    ### 类变量，直接通过DaspCommon.维护
    nodeID = ""
    IP = ""
    PORT = []
    adjID = []
    adjDirection = []
    adjDirectionOtherSide = []
    IPlist = []
    GUIinfo = ["localhost",0]    

    def __init__(self):
        pass

    def sendall_length(self, socket, head, data):
        '''
        为发送数据添加length报头
        '''
        length = "content-length:"+str(len(data)) + "\r\n\r\n"
        message = head + length + data
        socket.sendall(str.encode(message))

    def recv_length(self, conn):
        '''
        循环接收数据，直到收完报头中length长度的数据
        '''
        request = conn.recv(1024)
        message = bytes.decode(request)
        message_split = message.split('\r\n')
        content_length = message_split[1][15:]
        message_length =  len(message_split[0]) + len(message_split[1]) + 2*(len(message_split)-1) + int(content_length)
        while True:
            if len(message) < message_length:
                request = conn.recv(1024)
                message += bytes.decode(request)
            else:
                break
        return message

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