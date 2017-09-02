#!/usr/bin/env python3
# encoding=utf-8

## 时间：2017-9-1 ##
## 作者：孙士标 ##
## 博客地址：http://bbiao.me

import re
import codecs
import requests
from bs4 import BeautifulSoup

__author__ = 'sunshibiao'

pattern = re.compile('article block untagged mb15 typs_\w+')
url = 'http://www.qiushibaike.com/hot/'
def get_html(url):
    ''' 获取html '''
    html = requests.get(url).content
    return html

def get_page_list(html):
    ''' 构造所有的页面 '''

    next_page_url = url
    html = get_html(next_page_url)
    soup = BeautifulSoup(html, 'lxml')
    content = soup.find('ul', attrs={'class': 'pagination'})
    links = []
    each_pages = []
    for i in content.find_all('li'):
        if i.find('span', attrs={'class': 'page-numbers'}):
            nums = i.find('span', attrs={'class': 'page-numbers'})
            num = nums.getText()
            links.append(int(num))

    for link in range(1, links[-1]+1):
        each_page = next_page_url + 'page/' + str(link)
        each_pages.append(each_page)
    return each_pages

def get_text_or_pic(url):
    ''' 获取文本内容并写入文件, 如果是图片就保存图片 '''
    with codecs.open('duanzi', 'wb', 'utf-8') as fp:
        n = 1
        for i in url:
            html = get_html(i)
            soup = BeautifulSoup(html, 'lxml')
            content = soup.find('div', attrs={'id': 'content-left', 'class': 'col1'})
            text_lists = []
            for attr in set(re.findall(pattern, str(soup))):
                for text_list in content.find_all('div', attrs={'class': attr}):
                    if text_list.find('div', {'class': 'thumb'}):
                        img_link = text_list.find('div', {'class': 'thumb'})
                        img = img_link.find('img')['src']
                        rel_img = 'https:' + img
                        print('正在下载第%s张图片' % n)
                        filename = ('第%s张.jpg' % n)
                        with open(filename, 'wb+') as jpg:
                            jpg.write(requests.get(rel_img).content)
                        n += 1
                    else:
                        text = text_list.find('div', attrs={'class': 'content'}).find('span').getText()
                        text_lists.append(text)
            fp.write('{duanzi}'.format(duanzi='\n'.join(text_lists)))

def main():
  get_text_or_pic(get_page_list(get_html(url)))


if __name__ == '__main__':
    main()








