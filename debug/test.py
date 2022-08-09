import time,datetime
start =datetime.datetime.now()
time.sleep(10)
endtime =  datetime.datetime.now()
print((endtime-start).microseconds,endtime-start) 