class A():
    def __init__(self):
        global X
        X = 5

    def run(self):
        self.x.append("A2")

class B():
    def __init__(self,x):
        self.x = x
        self.x.append('B')

X = 3
a = A()
b = B(X)
a.run()
T = 1
