# -*- coding: utf-8 -*-
import os,re

sourceFilePath=os.path.abspath('app/res/source_data.html')

rawDataFilePath=os.path.abspath('app/res/raw_data2')
rawDataFile = open(rawDataFilePath, 'r')



mobileFilePath=os.path.abspath('app/res/mobile_data')
mobileFile=open(mobileFilePath,'w')
pattern = re.compile(u"1[34578]\d{9}")


def writemobile(item):
    mobileFile.write(item)
    mobileFile.write("\n")


# with open(rawDataFilePath) as file_object:
#      print(file_object.read())




print(rawDataFilePath)
# reader1 = rawDataFile.read()
# print(reader1)
while 1:
    line = rawDataFile.readline()
    print(line)

    if  line:
        phone = pattern.findall(line)
        if phone:
            writemobile(str(phone))
    else:
        break

mobileFile.close()
print("结束")

