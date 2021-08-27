from scipy.optimize import curve_fit
import pandas as pd
import os
from collections import OrderedDict
import math

# 输入：日期
# 输出：截取8点到19点的数据并修正温度

class room_process:
    def __init__(self, name, dir_path):
        self.dir_path = dir_path
        self.name = name + '_result.csv'
    
    def read_csv(self):
        files = os.listdir(self.dir_path)
        for file in files: 
            if file == self.name:
                self.df = pd.read_csv(self.dir_path + '/' + file)
                break
        starttime = 8*60
        endtime = 19*60
        self.df = self.df.iloc[starttime:endtime+1]
        self.total_cols = self.df.shape[1]
        self.total_rows = self.df.shape[0]
        self.col_list = list(self.df.columns)
        
    def process_data(self):
        deviation1 = self.df['room_temp1'].mean() - self.df['FCU_temp_feedback'].mean()
        deviation2 = self.df['room_temp2'].mean() - self.df['FCU_temp_feedback'].mean()
        print(self.name[0:6], "room_temp1 deviation", deviation1)
        print(self.name[0:6], "room_temp2 deviation", deviation2)
        
        if not math.isnan(deviation1) and not math.isnan(deviation1):
            c1 = self.col_list.index('room_temp1')
            c2 = self.col_list.index('room_temp2')
            for r in range(self.total_rows):
                # 需要保留2位小数
                self.df.iloc[r, c1] = round(self.df.iloc[r, c1] - deviation1,2)
                self.df.iloc[r, c2] = round(self.df.iloc[r, c2] - deviation2,2)

    def write_xlsx_results(self):
        writer = pd.ExcelWriter(self.dir_path + '/' + self.name[0:6] + '_result_fixed.xlsx')
        self.wdata = OrderedDict()
        for line in list(self.df.columns):
            self.wdata[line] = list(self.df[line])    #构建excel格式
        self.obj = pd.DataFrame(self.wdata)
        self.obj.to_excel(writer, self.name[0:6])
        writer.save()
    
    def write_csv_results(self):
        self.df.to_csv(self.dir_path + '/' + self.name[0:6] + '_result_fixed.csv',index=0) #不保存行索引


class pump_process:
    def __init__(self, name, dir_path):
        self.dir_path = dir_path
        self.name = name + '_result.csv'
    
    def read_csv(self):
        files = os.listdir(self.dir_path)
        for file in files: 
            if file == self.name:
                self.df = pd.read_csv(self.dir_path + '/' + file)
                break
        starttime = 8*60
        endtime = 19*60
        self.df = self.df.iloc[starttime:endtime+1]
        self.total_cols = self.df.shape[1]
        self.total_rows = self.df.shape[0]
        self.col_list = list(self.df.columns)

    def write_xlsx_results(self):
        writer = pd.ExcelWriter(self.dir_path + '/' + self.name[0:6] + '_result_fixed.xlsx')
        self.wdata = OrderedDict()
        for line in list(self.df.columns):
            self.wdata[line] = list(self.df[line])    #构建excel格式
        self.obj = pd.DataFrame(self.wdata)
        self.obj.to_excel(writer, self.name[0:6])
        writer.save()
    
    def write_csv_results(self):
        self.df.to_csv(self.dir_path + '/' + self.name[0:6] + '_result_fixed.csv',index=0) #不保存行索引
    
    def process_data(self):
        pass

class heatpump_process:
    def __init__(self, name, dir_path):
        self.dir_path = dir_path
        self.name = name + '_result.csv'
    
    def read_csv(self):
        files = os.listdir(self.dir_path)
        for file in files: 
            if file == self.name:
                self.df = pd.read_csv(self.dir_path + '/' + file)
                break
        starttime = 8*60
        endtime = 19*60
        self.df = self.df.iloc[starttime:endtime+1]
        self.total_cols = self.df.shape[1]
        self.total_rows = self.df.shape[0]
        self.col_list = list(self.df.columns)

    def write_xlsx_results(self):
        writer = pd.ExcelWriter(self.dir_path + '/' + self.name[0:10] + '_result_fixed.xlsx')
        self.wdata = OrderedDict()
        for line in list(self.df.columns):
            self.wdata[line] = list(self.df[line])    #构建excel格式
        self.obj = pd.DataFrame(self.wdata)
        self.obj.to_excel(writer, self.name[0:6])
        writer.save()
    
    def write_csv_results(self):
        self.df.to_csv(self.dir_path + '/' + self.name[0:10] + '_result_fixed.csv',index=0) #不保存行索引
    
    def process_data(self):
        pass

        
if __name__ == "__main__":
    date = "2021-08-16" 
    dir_path = 'DB_data/{}'.format(date)
    room1 = room_process('room_1', dir_path)
    room2 = room_process('room_2', dir_path)
    room3 = room_process('room_3', dir_path)
    room4 = room_process('room_4', dir_path)
    room5 = room_process('room_5', dir_path)
    room6 = room_process('room_6', dir_path)
    room7 = room_process('room_7', dir_path)
    room_list = [room1, room2, room3, room4, room5, room6, room7]
    pump1 = pump_process('pump_1', dir_path)
    hp1 = heatpump_process('heatpump_1', dir_path)

    for item in room_list:
        item.read_csv()        
        item.process_data()
        item.write_csv_results()
    pump1.read_csv()
    pump1.process_data()
    pump1.write_csv_results()
    hp1.read_csv()
    hp1.process_data()
    hp1.write_csv_results()