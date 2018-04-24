# -*- coding: utf-8 -*-
import os
from xlwt import *
mobileFilePath=os.path.abspath('app/res/mobile_data')
mobileFile=open(mobileFilePath,'r')

excelFilePath=os.path.abspath('app/res/excel_data')
excelFile=open(excelFilePath,'w')

#转excel
def excel_transfer():
    ws = Workbook(encoding='utf-8')
    w = ws.add_sheet(u"联系人方式")
    w.write(0, 0, u"手机号")
    excel_row = 1
    while 1:
        line = mobileFile.readline()
        print(line)

        if line:
            w.write(excel_row, 0, line)
            # w.write(excel_row, 1, data_singer_name)  
        else:
            break
        excel_row+=1
    ws.save(excelFile)

excel_transfer()