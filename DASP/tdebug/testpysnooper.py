import sys
import time
sys.path.insert(1,".") 
from pysnooper import snoop

@snoop(relative_time=True)
def A():
    for i in range(10):
        print (i)
        time.sleep(0.5)

A()