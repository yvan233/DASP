import socket
import ctypes
import inspect
class DaspFuncMixin():
    '''
    Dsp基础方法混合
    '''
    def __init__(self):
        pass

    def sendall_length(self, s, head, data):
        '''
        为发送数据添加length报头
        '''
        length = "content-length:"+str(len(data)) + "\r\n\r\n"
        message = head + length + data
        s.sendall(str.encode(message))

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

    def _async_raise(self, tid, exctype):
        '''
        抛出异常
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

class BaseServer(DaspFuncMixin):
    '''基础服务器

    Dsp基础服务器

    '''
    def __init__(self):
        pass

    def samlpe(self):
        '''基本描述

        详细描述

        Args:
            path (str): The path of the file to wrap
            field_storage (FileStorage): The :class:`FileStorage` instance to wrap
            temporary (bool): Whether or not to delete the file when the File instance is destructed

        Returns:
            BufferedFileStorage: A buffered writable file descriptor
        '''
        pass
