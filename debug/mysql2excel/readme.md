## 将备份文件转为excel的脚本库

0autoatart.py
自动启动脚本

1file2sql.py
将指定日期的数据库备份文件导入到本地的数据库中

2sql2csv.py
将本地数据库的数据导入到csv文件中，一个节点一个csv

3csv2excel.py
将多个csv文件整合成一个excel

4csv2plot.py
绘图

5data_process.py
处理间断点，0/1阶保持

6data_process_fixed.py
取8点到19点的数据，将IO温度拟合到面板温度附近

### 默认路径
DB_Backup 数据库备份文件夹

DB_data 导出文件夹，按日期区分文件夹

### 其他
db_backup.py
树莓派本地备份数据库的脚本

mysql2csv.py
直接将一个数据表导入到csv中

