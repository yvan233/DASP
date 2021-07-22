import time
from datetime import datetime

db_time = time.strftime("%Y-%m-%d %H:%M:%S")

#

cur_date = datetime.now().strftime("%Y%m%d")
zero_time = datetime(int(cur_date[0:4]), int(cur_date[4:6]), int(cur_date[6:8]), 0, 0)
print((datetime.now()-zero_time))