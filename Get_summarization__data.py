# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 11:17:31 2018

@author: DELL
"""
'''
文本摘要数据爬虫

           爬虫地址： https://www.yidaiyilu.gov.cn/slyww.htm#

           新闻开始时间为：2017-07-03

           爬取结果要求保存为json格式，  纯文本，标点符号保留；每段摘要需保存下面三个信息：

            summary：

            content:

            address:   

          网站2017-08-07之后的网页形式更换为新版本
'''

import time
import datetime
import six
import json
import argparse
from urllib import request
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq

now_time = datetime.datetime.now()
yes_time = now_time + datetime.timedelta(days=-1)
yesterday = yes_time.strftime('%Y-%m-%d')
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--start_time', help='get web data start time,Input example: 2018-08-15')
parser.add_argument('-e', '--end_time', default=yesterday,
                    help='get web data end time (default: yesterday),Input example: 2018-08-15')
parser.add_argument('-o', '--output', default='output.json',
                    help='Stored file name (default: summary.json),Input example: summary.json')
args = parser.parse_args()
# file_name = 'summar.json'
url = 'https://www.yidaiyilu.gov.cn/info/iList.jsp?tm_id=296&time='

class Get_web_data:
    def __init__(self, url, start_time, end_time):
        self.url = url
        self.beginDate = start_time
        self.endDate = end_time

    # get the datetime from2017-07-03 to 2018-09-10
    def dateRange(self,beginDate, endDate):
        dates = []
        dt = datetime.datetime.strptime(beginDate, "%Y-%m-%d")
        date = beginDate[:]
        while date <= endDate:
            dates.append(date)
            dt = dt + datetime.timedelta(1)
            date = dt.strftime("%Y-%m-%d")
        return dates

    # get the html arrow data from websets
    # '2017-07-03', '2018-09-10'
    def get_html_data(self):
        sum = 0
        for date in self.dateRange(self.beginDate, self.endDate):
            print('This time is :', date)
            # 构造头文件，模拟浏览器访问
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
            page = request.Request(self.url + date, headers=headers)
            page_info = request.urlopen(page).read().decode('utf-8')  # 打开Url,获取HttpResponse返回对象并读取其ResposneBody
            page_info_copy = page_info  # 复制page_info 数据
            page_info = BeautifulSoup(page_info, 'html.parser')
            if page_info.p == None: #判断P标签是否为空
                print('undo ', date)
                pass
            else:
                sum = sum + self.clean_html(page_info_copy, self.url, date)
            time.sleep(2)  # stop 3 scond
        print('the total of data number data: ', sum)


    def clean_html(self,page_info, url, date):
        doc = pq(page_info)
        for p in doc('p'):
            '''
            pyquery tools 筛选符合条件的<p>标签
    
            '''
            if doc(p).children('strong').size() == 3:
                doc(p).remove()

            if doc(p).children('strong span').size() >= 1:
                doc(p).remove()

            if doc(p).children('span strong').size() > 1:
                doc(p).remove()

            if doc(p).children('span').size() == 1:
                doc(p).remove()

            if doc(p).children('span').size() == 2:
                doc(p).remove()

            if pq(p).text() == '':
                doc(p).remove()

            if doc(p).children('img').size == 1:
                doc(p).remove()
            '''
    
            doc("[align= 'center']").remove()
    
    
            时间从2017-08-07后将是这条语句
    
            '''
            if date > '2017-08-06':
                doc("[align= 'center']").remove()

        sumandcont = []
        for p in doc('p'):
            sumandcont.append(doc(p).text())
            print(doc(p).text())
        number = self.to_json(sumandcont, url, date)
        return number


    # put the summaries,content and url to local as json file
    def to_json(self, sum_and_cont, url, date):
        number = 0
        if len(sum_and_cont[0]) > 50:
            del (sum_and_cont[0])
        else:
            for a, b in six.moves.zip(sum_and_cont[::2], sum_and_cont[1::2]):
                article = {
                    'summary': a,
                    'content': b,
                    'address': url + date,
                }
                if (len(article['content']) - len(
                        article['summary']) < 40):  # 判断如果content的长度 - summary的长度<40则这条网页信息解析出来的文本有误没跳过执行下提条
                    print('this is the error data web', date)
                    break
                else:
                    number = number + 1
                    with open(args.output, 'a+', encoding='utf-8') as file_object:
                        json.dump(article, file_object, ensure_ascii=False, indent=4)
        return number


if __name__ == '__main__':
    start_time = time.time()
    getwebdata = Get_web_data(url, args.start_time, args.end_time)
    getwebdata.get_html_data()
    end_time = time.time()
    print("the process total time:", end_time - start_time)

