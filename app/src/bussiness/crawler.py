# -*- coding: utf-8 -*-
import HTMLParser,sys,os,string
sourceFilePath=os.path.abspath('app/res/source_data.html')
rawDataFilePath=os.path.abspath('app/res/raw_data')
rawDataFile = open(rawDataFilePath, 'w')
tagstack=[]
class ShowStructure(HTMLParser.HTMLParser):
    def handle_starttag(self, tag, attrs):
        tagstack.append(tag)

    def handle_endtag(self, tag):
        tagstack.pop()

    def handle_data(self, data):
        if data.strip():
            for tag in tagstack:
                if tag=='h2':
                    sys.stdout.write(data+"\n")
                    rawDataFile.write(data+'\n')





ShowStructure().feed(open(sourceFilePath, 'r').read())



# sys.stdout.write('/' + tag)
#             sys.stdout.write(' >> %s/n' % data[:40].strip())
# 一、常用属性和方法介绍
#
# 　　HtmlParser是一个类，在使用时一般继承它然后重载它的方法，来达到解析出需要的数据的目的。
#
# 　　1.常用属性：
#
# 　　　　lasttag，保存上一个解析的标签名，是字符串。
#
# 　　2.常用方法：　
#
# 　　　　handle_starttag(tag, attrs) ，处理开始标签，比如<div>；这里的attrs获取到的是属性列表，属性以元组的方式展示
# 　　　　handle_endtag(tag) ，处理结束标签,比如</div>
# 　　　　handle_startendtag(tag, attrs) ，处理自己结束的标签，如<img />
# 　　　　handle_data(data) ，处理数据，标签之间的文本
# 　　　　handle_comment(data) ，处理注释，<!-- -->之间的文本

