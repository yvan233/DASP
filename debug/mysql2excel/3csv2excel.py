import pandas as pd
import os
from collections import OrderedDict

if __name__ == "__main__":
    date = "2021-08-14"
    dir_path = 'DB_data/{}'.format(date)
    writer = pd.ExcelWriter('{}/{}.xlsx'.format(dir_path, date))
    files= os.listdir(dir_path) 
    for file in files: 
        if file[-4:] == '.csv':
            df = pd.read_csv(dir_path + '/' + file)
            data = OrderedDict()
            for line in list(df.columns):
                data[line] = list(df[line])    #构建excel格式
            obj = pd.DataFrame(data)
            obj.to_excel(writer, file)
    writer.save()
