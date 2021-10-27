import os,time,datetime

#数据库ip或者域名
host="localhost"
#数据库用户名
username="root"
#数据库密码
password="cfins"
#数据库端口
port="3306"
#备份目录
dirPath="D:/db_backup"
#数据库备份保留天数
maxBackupDays=90
#在备份后删除过期备份，False则在备份前删除过期备份
deleteAfterBackup=True

def deleteDir(path):
    "递归删除文件和文件夹"
    if(os.path.exists(path)):
        if(os.path.isdir(path)):
            fps=os.listdir(path)
            for fp in fps:
                deleteDir(path+"/"+fp)
            os.rmdir(path)
        else:
            os.remove(path)

def deleteTooManyBackup():
    "删除过多的备份"
    global maxBackupDays,dirPath
    obj=datetime.datetime.now()-datetime.timedelta(days=maxBackupDays-1)
    title=obj.strftime("%Y%m%d")
    fps=os.listdir(dirPath)
    for temp in fps:
        try:
            if(int(temp)<int(title)):
                #删除该备份
                deleteDir(dirPath+"/"+temp)
        except Exception as err:
            pass

def index(db,d,t):
    "利用mysqldump备份数据库"
    global host,username,password,port,dirPath
    #mysqldump -h ip -P 端口 -u 用户名 -p密码 数据库名字 | gzip > 备份目录/当前日期/时间_数据库名字.sql.gz
    command="mysqldump -h %s -P %s -u %s -p%s %s | gzip >  %s/%s/%s_%s.sql.gz"%(host,port,username,password,db,dirPath,d,t,db)
    # mysqldump -hhostname -uusername -ppassword databasename | gzip > backupfile.sql.gz
    command ="gzip -d < DB_Backup/room_2/2021-08-08/00_00_45_data.sql.gz | mysql -uroot -pDSPadmin data_node2"
    # gunzip < backupfile.sql.gz | mysql -uusername -ppassword databasename
    # gzip -d < 00_00_45_data.sql.gz | mysql -uroot -pDSPadmin data_node2
    os.system(command)
    print ("备份文件生成完毕!")

def backup_start(dbList):
    "入口函数"
    global deleteAfterBackup,dirPath

    d=time.strftime("%Y%m%d")
    t=time.strftime("%H%M%S")
    path="%s/%s"%(dirPath,d)
    if(not os.path.exists(path)):
        os.makedirs(path)

    if(not deleteAfterBackup):
        deleteTooManyBackup()
    for dbName in dbList:
        index(dbName,d,t)
    if(deleteAfterBackup):
        deleteTooManyBackup()

if __name__ == "__main__":
    backup_start(['data'])
