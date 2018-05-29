from selenium import webdriver
import time
import re
import requests
from urllib import parse
import qq_init as qq


class Spider(object):
    def __init__(self):
        self.ids = ''
        self.uins = ''
        self.driver = webdriver.PhantomJS()
        self.driver.get('https://i.qq.com/')
        self.__username = qq.qq
        self.__password = qq.mm
        self.headers = {
            'origin': 'https://user.qzone.qq.com',
            'referer': 'https://user.qzone.qq.com',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        }
        self.req = requests.Session()
        self.cookies = {}

    def login(self):
        self.driver.switch_to.frame('login_frame')
        self.driver.find_element_by_id('switcher_plogin').click()
        self.driver.find_element_by_id('u').clear()
        self.driver.find_element_by_id('u').send_keys(self.__username)
        self.driver.find_element_by_id('p').clear()
        self.driver.find_element_by_id('p').send_keys(self.__password)
        self.driver.find_element_by_id('login_button').click()
        time.sleep(2)
        self.driver.implicitly_wait(2)
        cookie = ''
        for item in self.driver.get_cookies():
            cookie += item["name"] + '=' + item['value'] + ';'
        self.cookies = cookie
        self.get_g_tk()
        self.headers['Cookie'] = self.cookies
        self.get_ids()
        self.driver.quit()

    def get_g_tk(self):
        p_skey = self.cookies[self.cookies.find('p_skey=') + 7: self.cookies.find(';', self.cookies.find('p_skey='))]
        h = 5381
        for i in p_skey:
            h += (h << 5) + ord(i)
        print('g_tk', h & 2147483647)
        self.g_tk = h & 2147483647

    def get_ids(self):
        url = 'https://user.qzone.qq.com/proxy/domain/m.qzone.qq.com/cgi-bin/new/get_msgb?'
        params = {
            'uin': self.__username,
            'hostUin': self.__username,
            'inCharset': 'utf-8',
            'outCharset': 'utf-8',
            'sort': 0,
            'num': 10,
            'format': 'jsonp',
            'g_tk': self.g_tk
        }
        url = url + parse.urlencode(params)
        t = True
        start = 0
        while t:
            url_ = url + '&start=' + str(start)
            board = self.req.get(url_, headers=self.headers)
            time.sleep(1)    # 设置时间阈值，防止ip被封
            if '\"commentList\":[]' in board.text:
                t = False
            else:
                ids = re.findall('"id":".*?"', board.text)
                uins = re.findall('"uin":\d+', str(re.findall('type.*\n"uin":\d+', board.text)))
                for id, uin in zip(ids, uins):
                    print(id, uin)
                    self.ids += id.replace('"id":', '').replace('"', '') + ","
                    self.uins += uin.replace('"uin":', '') + ','
                start += 10

    def del_board(self):
        print(self.ids, self.uins)
        url = 'https://h5.qzone.qq.com/proxy/domain/m.qzone.qq.com/cgi-bin/new/del_msgb?' + '&g_tk=' + str(self.g_tk)
        data = {
            'hostUin': self.__username,
            'idList': self.ids,
            'uinList': self.uins,
            'iNotice': 1,
            'inCharset': 'utf-8',
            'outCharset': 'utf-8',
            'ref': 'qzone',
            'json': 1,
            'g_tk': self.g_tk,
            'format': 'fs',
            'qzreferrer': 'https://qzs.qq.com/qzone/msgboard/msgbcanvas.html'
        }
        response = self.req.post(url, data=data, headers=self.headers).text
        if '"message":"成功删除' in response:
            print('所有留言删除成功。')
        else:
            print('出现错误')

if __name__ == '__main__':
    sp = Spider()
    sp.login()
    sp.del_board()
