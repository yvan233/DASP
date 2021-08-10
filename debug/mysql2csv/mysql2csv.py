# mysql 存储成 csv脚本
import pymysql
import csv

def from_mysql_get_all_info():
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        db='data_node2',
        password='DSPadmin')
    cursor = conn.cursor()
    sql = 'select * from sensor_room_his'
    cursor.execute(sql.encode('utf-8'))
    data = cursor.fetchall()
    conn.close()
    return data


def write_csv():
    data = from_mysql_get_all_info()
    filename = 'data/sensor_room_his.csv'
    with open(filename,mode='w',newline="",encoding='utf-8') as f:
        write = csv.writer(f,dialect='excel')
        for item in data:
            item = list(item)
            item[0] = item[0].replace(u'\xa0', u' ')
            write.writerow(item)
write_csv()