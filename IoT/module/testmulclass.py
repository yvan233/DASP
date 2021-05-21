import threading
class FbPageRollback:
    def __init__(self):
        self.i = 0
    def run(self):
        for j in range(10):
            self.i = self.i + 1
            print (self.i)

if __name__ == '__main__':
    threads = []
    for i in range(4):
        rollback_obj = FbPageRollback()
        t = threading.Thread(target=rollback_obj.run,args=())
        threads.append(t)
    for i in range(4):
        threads[i].start()
