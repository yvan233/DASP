# mysql 存储成 csv脚本  转化成二维数据
import pymysql
import csv
from datetime import datetime

nodename = "node11"
tablename = "heatpump_panel_his"
datalenth = 2  # 数据库中数据长度

def from_mysql_get_all_info():
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        db='data_{}'.format(nodename),
        password='DSPadmin')
    cursor = conn.cursor()
    sql = 'select * from {}'.format(tablename)
    cursor.execute(sql.encode('utf-8'))
    data = cursor.fetchall()
    conn.close()
    return data


def write_csv():
    data = from_mysql_get_all_info()
    filename = 'data/{}_{}.csv'.format(nodename,tablename)
    with open(filename,mode='w',newline="",encoding='utf-8') as f:
        write = csv.writer(f,dialect='excel')
        line = []
        line.append('time')
        for j in range(datalenth):
            line.append(data[j][2])
        write.writerow(line)
        i = 0
        while (i < len(data)):
            time = datetime.strptime(data[i][0],"%Y-%m-%d %H:%M:%S")
            if time.hour >= 4 and time.hour < 22:
                line = []
                # line.append(data[i][0].replace(u'\xa0', u' '))
                line.append(data[i][0][11:16])
                for j in range(datalenth):
                    line.append(data[i+j][3])
                write.writerow(line)
                i += datalenth
            else:
                i += 1
write_csv()