#!/usr/bin/env python3
# encoding=utf-8

# 作者：孙士标
# 博客地址：http://bbiao.me
# 日期：2017-9-3

import os
import time
import requests
from bs4 import BeautifulSoup

__author__ = 'sunshibiao'

url = 'http://www.mmjpg.com'

def get_html(url):
    '''
    :解析主网页:
    :返回HTML源代码:
    '''
    # 获取网址源代码
    html = requests.get(url).content
    soup = BeautifulSoup(html, 'lxml')
    # 找到当前页的相册集链接所在的标签
    pic = soup.find('div', attrs={'class': 'pic'})
    return pic

def get_page(html):
    '''
    :获取所有页面:
    :并返回:
    '''
    page_link = html.find('div', attrs={'class': 'page'})
    last_page = page_link.find('a', attrs={'class': 'last'})['href']
    # 提取总页数
    total_page = last_page[6:]
    each_pages = []
    # 循环构造所有页面的链接，并放在名称为each_pages的列表里面
    for i in range(1, int(total_page)):
        each_page = url + '/home/' + str(i)
        each_pages.append(each_page)
    return each_pages

def get_link_list(html):
    '''
    :获去当前页面的所有图片链接:
    :并返回:
    '''
    links = []
    # 从当前页提取所有的相册集链接，放在名称为links的列表里
    link_list = html.find('ul')
    for i in link_list.find_all('li'):
        link = i.find('a')['href']
        links.append(link)
    return links

def get_detail_html(url):
    '''
    :获取详情页的HTML源代码:
    '''
    # 处理详情页
    html = requests.get(url).content
    soup = BeautifulSoup(html, 'lxml')
    content = soup.find('div', attrs={'class': 'main'})
    return content

def get_detail_page(html):
    '''
    :获取单个相册图片总数:
    :返回总数:
    '''
    # 提取详情页中的翻页，返回每一个相册集中的图片总数
    page_list = html.find('div', attrs={'class': 'page', 'id': 'page'})
    pages = []
    for i in page_list.find_all('a'):
        page = i.getText()
        pages.append(page)
    return int(pages[-2])

def get_detail_pic_link(html, links):
    '''
    :获取单个相册集中的所有相册页面:
    :返回相册中所有单页的链接:
    '''
    each_pics = []
    # 提取单个相册集中的图片总数，通过循环构造每个单页的链接
    pages = html.find('div', attrs={'class': 'page', 'id': 'page'}).find_all('a')
    all_page = int(pages[-2].getText())
    for i in range(1, all_page):
        each_pic = links + '/' + str(i)
        each_pics.append(each_pic)
    return each_pics

def main():
    # 所有页的循环
    for i in get_page(get_html(url)):
        # 每一页中的相册集链接的循环
        for j in get_link_list(get_html(i)):
            # 捕获任何异常，不处理，直接跳过(不一定有异常，但是这样写以防万一)
            try:
                # 调用读取详情页的函数
                detail_html = get_detail_html(j)
                # 获取每一个相册集的名称
                title = detail_html.find('div', attrs={'class': 'article'}).find('h2').getText()
                # 获取每一个相册集中所包含的图片总数
                total = get_detail_page(detail_html)
                # 创建以相册集名称为标题的文件夹
                dirname = u'[{}P] {}'.format(total, title)
                os.mkdir(dirname)
                # 通过调用获取单个相册集中的所有相册页面的函数，从详情页中提取每一张图片所在的链接
                each_pic = get_detail_pic_link(detail_html, j)
                n = 1
                # 循环处理每一个图片链接
                for k in each_pic:
                    pic = get_detail_html(k)
                    # 提出图片链接所在位置
                    picture = pic.find('div', attrs={'class': 'content', 'id': 'content'}).find('a').find('img')['src']
                    # 打印输出内容，图片保存位置
                    filename = '%s/%s/%s.jpg' % (os.path.abspath('.'), dirname, n)
                    print(u'开始下载图片:%s 第%s张' % (dirname, n))
                    # 写入文件，处理防盗链，通过加上User-Agent，和Referer，不加得到的图片会被重定向
                    with open(filename, 'wb+') as jpg:
                        jpg.write(requests.get(picture, headers={
                            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
                            'Referer': 'http://www.baidu.com'}).content)
                        # 设置单个图片下载时间
                        time.sleep(1)
                    n += 1
            except:
                pass

if __name__ == '__main__':
    main()