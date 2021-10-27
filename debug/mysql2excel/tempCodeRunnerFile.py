from datetime import datetime             
ele = "2021-06-21 23:03:27"
time = datetime.strptime(ele,"%Y-%m-%d %H:%M:%S")

print(datetime.strftime(time,"%m-%d"))