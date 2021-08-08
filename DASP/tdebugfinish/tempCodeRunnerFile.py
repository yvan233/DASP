# # 测试队列模块
import queue
q=queue.Queue()    #如果不设置长度,默认为无限长
print(q.maxsize)    #注意没有括号
q.put({"date":"12.123.1.23.123.123"})
q.put({"date":"12.123.1.23"})
print(q.queue)
if not q.empty():
    print(q.get())

if not q.empty():
    print(q.get())