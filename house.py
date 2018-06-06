import requests
import re
from bs4 import BeautifulSoup
import pymysql

class House:
    def __init__(self):
        try:
            self.db = pymysql.connect(host='localhost', user='root', password='', db='house', charset='utf8', port=3306)
            self.cursor = self.db.cursor()
        except pymysql.MySQLError as e:
            print(e.args)
        self.pages = list(range(1, 110))
        self.proxyHost = ""
        self.proxyPort = ""
        self.proxyUser = ""
        self.proxyPass = ""

    def get_html(self):
        while self.pages:
            url = 'http://xj.ganji.com/fang5/o'+str(self.pages[0])+'/'
            headers = {
                'Host': 'xj.ganji.com',
                'Referer': 'http://xj.ganji.com',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
            }
            proxy = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
                      "host": self.proxyHost,
                      "port": self.proxyPort,
                      "user": self.proxyUser,
                      "pass": self.proxyPass,
                    }
            proxies = {
                'http':  proxy,
                'https': proxy
            }
            html = requests.get(url, headers=headers, proxies=proxies).text
            if 'Cache Access Denied.' in html or '访问过于频繁，本次访问做以下验证码校验' in html:
                pass
            else:
                with open(str(self.pages[0]) + '.html', 'w', encoding='utf-8') as ht:
                    ht.write(html)
                    self.pages.remove(self.pages[0])

    def get_info(self):
        for page in range(1, 110):
            soup = BeautifulSoup(open('html/'+str(page)+'.html'), 'lxml')
            name = soup.findAll(class_='dd-item title')
            url = soup.findAll(class_='f-list-item ershoufang-list')
            community = soup.findAll(class_='area')
            DoorModel = soup.findAll(class_='dd-item size')
            AreaSize = soup.findAll(class_='dd-item size')
            price = soup.findAll(class_='num js-price')
            UnintPrice = soup.findAll(class_='time')
            area = soup.findAll(class_='address-eara')

            for i, j, k, l, m, n, o, p in zip(name, url, community, DoorModel, AreaSize, price, UnintPrice, area):
                title = i.find('a').getText()
                address = j['href'] if 'http' in j['href'] else 'http://xj.ganji.com' + j['href']
                xiaoqu = re.sub('(\(.*|\.\.\.)', '', k.getText().split('-')[0].strip()).replace('小区', '')
                huxing = l['data-huxing']
                mianji = m['data-area'].replace('㎡', '平')
                zongjia = n.getText()
                danjia = o.getText().replace('元/㎡', '')
                quyu = re.sub('\(.*', '', p.getText().split('-')[-1].strip().replace('二手房出售', ''))
                print('名称:', title, '地址:', address, '小区:', xiaoqu, '户型:', huxing, '面积:', mianji,
                      '总价:', zongjia, '单价:', danjia, '区域:', quyu)
                sql = 'insert into info(名称, 地址, 小区, 户型, 面积, 总价, 单价, 区域) values (%s, %s, %s, %s, %s, %s, %s, %s)'
                try:
                    self.cursor.execute(sql, (title, address, xiaoqu, huxing, mianji, float(zongjia), float(danjia), quyu))
                    self.db.commit()
                except pymysql.MySQLError as e:
                    print(e.args)
                    self.db.rollback()

            if len(self.pages) > 0:
                self.pages.remove(self.pages[0])

if __name__ == '__main__':
    hs = House()
    hs.get_html()
    hs.get_info()
