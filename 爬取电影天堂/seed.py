#!/usr/bin/env python3
# encoding=utf-8

## 时间：2017-9-17 ##
## 博客地址：http://bbiao.me ##
## 该代码所在文章： http://bbiao.me/爬取《电影天堂》所有电影种子  ##


__author__'sunshibiao'


import requests
from bs4 import BeautifulSoup

links = []
with open('电影种子', 'w+') as fp:
    for link in range(1, 11471):
        try:
            rel_url = 'http://www.btbtdy.com/down/' + str(link) + '-0-0.html'
            html = requests.get(rel_url).content
            soup = BeautifulSoup(html, 'lxml')
            title = soup.find('h1').getText()
            downlist = soup.find('form', attrs={'name': 'form2', 'id': 'form2'}).find('input')['value']
            data = {
                '电影名称:': title,
                '种子链接:': downlist
            }
            fp.write(str(data)+'\n')
            print(data)
        except:
            pass
