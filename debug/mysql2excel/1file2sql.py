# 将指定日期的数据库备份文件导入到本地不同的数据库中
# 当天的数据存储在后一天的文件夹中
# windows系统需安装gzip.exe
import os,sys
date = sys.argv[1]
nodenamelist = ["room_1","room_2","room_3","room_4","room_5","room_6","room_7","pump_1","heatpump_1"]
for nodename in nodenamelist:
    def _get_all_files_in_local_dir(local_dir):
        all_files = list()
        for root, dirs, files in os.walk(local_dir, topdown=True):
            for file in files:
                filename = os.path.join(root, file)
                all_files.append(filename)
        return all_files
    local_dir = "DB_Backup/{}/{}".format(nodename, date)
    sqlfile = _get_all_files_in_local_dir(local_dir)[0]
    sqlfile = sqlfile.replace('\\', '/')
    command ="gzip -d < {} | mysql -uroot -pDSPadmin data_{}".format(sqlfile, nodename)
    os.system(command)