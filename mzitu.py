#!/usr/bin/env python3
# encoding=utf-8

# 作者：孙士标
# 博客地址：http://bbiao.me
# 日期：2017-9-24

from bs4 import BeautifulSoup
import requests
import os
import time
from multiprocessing.pool import Pool

headers={
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Referer': 'http://www.mzitu.com/'
}
def get_pic(pag):
    url = 'http://www.mzitu.com/page/' + str(pag)
    html = requests.get(url,  headers=headers).content
    soup = BeautifulSoup(html, 'lxml')
    links = soup.find('ul', attrs={'id': 'pins'}).find_all('li')
    for link in links:
        n = 1
        title = link.find('span').getText()
        detail_link = link.find('a')['href']
        xml = requests.get(detail_link).content
        soups = BeautifulSoup(xml, 'lxml')
        pages = soups.find('div', attrs={'class': 'pagenavi'}).find_all('span')[-2].getText()
        dirname = u'[{}P] {}'.format(int(pages), title)
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        for page in range(1, int(pages)+1):
            each_pic = detail_link + '/' + str(page)
            picture = requests.get(each_pic, headers=headers).content
            pic_html = BeautifulSoup(picture, 'lxml')
            img = pic_html.find('div', attrs={'class': 'main-image'}).find('img')['src']
            filename = '%s/%s/%s.jpg' % (os.path.abspath('.'), dirname, n)
            print(u'开始下载图片:%s 第%s张' % (dirname, n))
            try:
                with open(filename, 'wb+') as jpg:
                    jpg.write(requests.get(img, headers=headers).content)
                n += 1
                time.sleep(1)
            except:
                pass

if __name__ == '__main__':
    pool = Pool(10)
    page = [x for x in range(1, 154)]
    pool.map(get_pic, page)
    pool.close()
    pool.join()
