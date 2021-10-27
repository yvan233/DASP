import pymysql
db=pymysql.connect(host='192.168.4.34',user='root',password='cfins',database='data')
cursor=db.cursor()

#查出数据库中所有表名称
cursor.execute("show tables")
table_name=cursor.fetchall()

for i in range(len(table_name)):
    # 修改字段类型
    sql = "ALTER TABLE %s MODIFY value varchar(50)"%(table_name[i])
    cursor.execute(sql)
    db.commit()
cursor.close()
db.close()