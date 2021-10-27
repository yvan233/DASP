from scipy.optimize import curve_fit
import pandas as pd
import os,sys
from collections import OrderedDict
import math

# input: time(step), fcu_control_feedback, room_temp， fcu_temp_feedback
# output: response models of different step responses
# comment: each model output has its start time(step), end time(step), model structure, parameters of the model and fitting parameters

class room_process:
    def __init__(self, name, dir_path):
        self.dir_path = dir_path
        self.name = name + '.csv'
    
    def read_csv(self):
        files = os.listdir(self.dir_path)
        for file in files: 
            if file == self.name:
                self.df = pd.read_csv(self.dir_path + '/' + file)
                break
        self.total_cols = self.df.shape[1]
        self.total_rows = self.df.shape[0]
        self.col_list = list(self.df.columns)
    def process_data(self):
        self.first_hold_cols = ['supply_pressure', 'return_pressure', 'waterflow', 'supply_temp', 'return_temp',
                          'room_temp1', 'room_RH1', 'room_temp2', 'room_RH2', 'differential_pressure']
        for c in range(self.total_cols):
            # 1-order-hold
            if self.col_list[c] in self.first_hold_cols:
                self.df.iloc[0,c] = self.df.iloc[1,c]
                if isinstance(self.df.iloc[0,c], float):
                    flag = 0
                    r_start = 0
                    r_end = 0
                    r_count = 0
                    for r in range(1, self.total_rows):
                        if math.isnan(self.df.iloc[r,c]) and self.df.iloc[r-1,c] < float('inf') and flag == 0:
                            flag = 1
                            r_start = r-1
                        elif math.isnan(self.df.iloc[r-1,c]) and self.df.iloc[r,c] < float('inf') and flag == 1:
                            flag = 0
                            r_end = r
                            r_count = r_end - r_start
                            dif_total = self.df.iloc[r_end, c] - self.df.iloc[r_start, c]
                            dif_each = dif_total / r_count
                            for i in range(1, r_count):
                                # 需要保留2位小数
                                self.df.iloc[r_start+i, c] = round(self.df.iloc[r_start, c] + i*dif_each,2)
                    else:
                        continue
            
            # 0-order-hold
            elif isinstance(self.df.iloc[0,c], float):
                self.df.iloc[0,c] = self.df.iloc[1,c]
                for r in range(1, self.total_rows):
                    if math.isnan(self.df.iloc[r,c]):
                        self.df.iloc[r,c] = self.df.iloc[r-1,c]    
    
    def write_xlsx_results(self):
        writer = pd.ExcelWriter(self.dir_path + '/' + self.name[0:6] + '_result.xlsx')
        self.wdata = OrderedDict()
        for line in list(self.df.columns):
            self.wdata[line] = list(self.df[line])    #构建excel格式
        self.obj = pd.DataFrame(self.wdata)
        self.obj.to_excel(writer, self.name[0:6])
        writer.save()
    
    def write_csv_results(self):
        self.df.to_csv(self.dir_path + '/' + self.name[0:6] + '_result.csv',index=0) #不保存行索引


class pump_process:
    def __init__(self, name, dir_path):
        self.dir_path = dir_path
        self.name = name + '.csv'
    
    def read_csv(self):
        files = os.listdir(self.dir_path)
        for file in files: 
            if file == self.name:
                self.df = pd.read_csv(self.dir_path + '/' + file)
                break
        self.total_cols = self.df.shape[1]
        self.total_rows = self.df.shape[0]
        self.col_list = list(self.df.columns)

    def write_xlsx_results(self):
        writer = pd.ExcelWriter(self.dir_path + '/' + self.name[0:6] + '_result.xlsx')
        self.wdata = OrderedDict()
        for line in list(self.df.columns):
            self.wdata[line] = list(self.df[line])    #构建excel格式
        self.obj = pd.DataFrame(self.wdata)
        self.obj.to_excel(writer, self.name[0:6])
        writer.save()
    
    def write_csv_results(self):
        self.df.to_csv(self.dir_path + '/' + self.name[0:6] + '_result.csv',index=0) #不保存行索引
    
    def process_data(self):
        self.power_list = ['Active_power', 'Reactive_power', 'Apparent_power']
        for c in range(self.total_cols):
            self.df.iloc[0,c] = self.df.iloc[1,c]
            for r in range(1, self.total_rows):
                if isinstance(self.df.iloc[r,c], str) or math.isnan(self.df.iloc[r,c]):
                    self.df.iloc[r,c] = self.df.iloc[r-1,c]


class heatpump_process:
    def __init__(self, name, dir_path):
        self.dir_path = dir_path
        self.name = name + '.csv'
    
    def read_csv(self):
        files = os.listdir(self.dir_path)
        for file in files: 
            if file == self.name:
                self.df = pd.read_csv(self.dir_path + '/' + file)
                break
        self.total_cols = self.df.shape[1]
        self.total_rows = self.df.shape[0]
        self.col_list = list(self.df.columns)

    def write_xlsx_results(self):
        writer = pd.ExcelWriter(self.dir_path + '/' + self.name[0:10] + '_result.xlsx')
        self.wdata = OrderedDict()
        for line in list(self.df.columns):
            self.wdata[line] = list(self.df[line])    #构建excel格式
        self.obj = pd.DataFrame(self.wdata)
        self.obj.to_excel(writer, self.name[0:6])
        writer.save()
    
    def write_csv_results(self):
        self.df.to_csv(self.dir_path + '/' + self.name[0:10] + '_result.csv',index=0) #不保存行索引
    
    def process_data(self):
        for c in range(self.total_cols):
            self.df.iloc[0,c] = self.df.iloc[1,c]
            for r in range(1, self.total_rows):
                if isinstance(self.df.iloc[r,c], str) or math.isnan(self.df.iloc[r,c]):
                    self.df.iloc[r,c] = self.df.iloc[r-1,c]

        

date = sys.argv[1]
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