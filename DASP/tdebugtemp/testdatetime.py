from datetime import datetime,timedelta
date = datetime.now()
cur_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
# print(date, cur_date)

d1 = '2021-07-26 01:44:51.143242'
d2 = '2021-07-26 01:44:53.163242'
d3 = '2021-07-26 01:44:54.173242'
d4 = '2021-07-26 01:44:57.233242'

d1 = datetime.strptime(d1,"%Y-%m-%d %H:%M:%S.%f")
d2 = datetime.strptime(d2,"%Y-%m-%d %H:%M:%S.%f")
d3 = datetime.strptime(d3,"%Y-%m-%d %H:%M:%S.%f")
d4 = datetime.strptime(d4,"%Y-%m-%d %H:%M:%S.%f")

tmp = timedelta(milliseconds=50)
tmp2 = timedelta(milliseconds=-50)
offset = (d2-d1+d3-d4)/2
if offset < timedelta(seconds=0): 
    print("-{}".format(-offset))
if offset >= tmp2 and offset <= tmp:
    print("small than 0.05s")
else:
    print("need update")


print(offset)


theta = (d2-d1+d4-d3)/2
real_time = d3+theta
settime = real_time.strftime("%Y-%m-%d %H:%M:%S.%f")
print (theta,settime)
a = 1
# 写法回头参考github，正式一些


a = []
print(a.pop())
