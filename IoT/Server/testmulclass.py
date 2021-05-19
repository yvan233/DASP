import threading
class FbPageRollback:
    def __init__(self):
    	pass
    def run(self):
    	for i in range(10):
    		print(i)

if __name__ == '__main__':
    rollback_obj = FbPageRollback()
    threads = []
    for i in range(4):
        t = threading.Thread(target=rollback_obj.run,args=())
        threads.append(t)
    for i in range(4):
        threads[i].start()
