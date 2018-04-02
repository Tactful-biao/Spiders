import requests
from bs4 import BeautifulSoup
import sys
import re

keyword = sys.argv[1]
class Movies:
    def __init__(self):
        self.url = 'http://btdb.to/q/' + keyword + '/' + '1' + '?sort=popular'
        self.url2 = 'https://btso.pw/search/' + keyword
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Host': 'btdb.to',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        }

    def movie(self):
        html = requests.get(self.url, headers=self.headers).text
        soup = BeautifulSoup(html, 'lxml')
        li = soup.find('ul', attrs={'class': 'search-ret-list'}).findAll('li', attrs={'class': 'search-ret-item'})
        for i in li:
            title = i.find('a')['title']
            size = i.find('div', attrs={'class': 'item-meta-info'}).find('span').getText()
            time = i.find('div', attrs={'class': 'item-meta-info'}).find_all('span')[2].getText()
            link = i.find('div', attrs={'class': 'item-meta-info'}).find('a')['href']
            link = link.replace(re.search('&.*', link).group(), '')
            print(title, link, size, time)

    def movie2(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Host': 'btso.pw',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        }
        html = requests.get(self.url2, headers=headers).text
        soup = BeautifulSoup(html, 'lxml')
        row = soup.find('div', attrs={'class': 'data-list'}).find_all('div', attrs={'class': "row"})
        for i in row[1:]:
            title = i.find('a')['title']
            link = i.find('a')['href'].replace('https://btso.pw/magnet/detail/hash/', 'magnet:?xt=urn:btih:')
            size = i.find('div', attrs={'class': 'col-sm-2 col-lg-1 hidden-xs text-right size'}).getText()
            time = i.find('div', attrs={'class': 'col-sm-2 col-lg-2 hidden-xs text-right date'}).getText()
            print(title, link, size, time)

if __name__ == '__main__':
    movie = Movies()
    movie.movie()
    movie.movie2()
