import pandas as pd
import openpyxl
import os

def csv_to_xlsx_pd(src_path):
    dst_path = src_path.split('.csv')[0] + '.xls'
    csv = pd.read_csv(src_path, encoding='utf-8')
    csv.to_excel(dst_path, index=False)


if __name__ == '__main__':
    l = os.listdir('./')
    for f in l:
        print(os.path.splitext(f))
        if os.path.splitext(f)[1] == '.csv':
            print(f)
            csv_to_xlsx_pd(f)
        
