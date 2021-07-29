# 测试是否会对传进类里的变量进行更改
# 测试结果，传过来的类里的变量可以被改变
class A:
    def __init__(self):
        self.I = 1
        
class B:
    def __init__(self, a):
        self.a = a
    def run(self):
        self.a.I = 2

class C:
    def __init__(self, a):
        self.a = a
    def run(self):
        self.a.I = 1

a = A()
b = B(a)
c = C(a)
b.run()
c.run()
print (a.I)