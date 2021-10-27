# # 测试队列模块
import queue
q=queue.Queue()    #如果不设置长度,默认为无限长
print(q.maxsize)    #注意没有括号
q.put({"date":"12.123.1.23.123.123"})
q.put({"date":"12.123.1.23"})
print(q.queue)
if not q.empty():
    print(q.get_nowait())

if not q.empty():
    print(q.get_nowait())

if not q.empty():
    print(q.get_nowait())
# while True:
#     q.get()  #阻塞形式

a = [1,[2,3]]
a[1].append(1)
print(a)

# path = [1,2,3,4,5]
# nextnode = path.pop()
# print(nextnode, path)

path = [1,2,34]
data = 1
data = {
    "key": "DescendantData",
    "DAPPname": "DAPPname",
    "path": path,
    "134":data
}
# 如果指定了路径
print(data)
nextnode = path.pop()
print(data)