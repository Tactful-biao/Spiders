from selenium import webdriver
import time
import re
import requests
from urllib import parse
import qq_init as qq


class Spider(object):
    def __init__(self):
        self.tids = []
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
        self.get_tids()
        self.driver.quit()

    def get_g_tk(self):
        p_skey = self.cookies[self.cookies.find('p_skey=') + 7: self.cookies.find(';', self.cookies.find('p_skey='))]
        h = 5381
        for i in p_skey:
            h += (h << 5) + ord(i)
        print('g_tk', h & 2147483647)
        self.g_tk = h & 2147483647

    def get_tids(self):
        url = 'https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?'
        params = {
            'uin': self.__username,
            'inCharset': 'utf-8',
            'outCharset': 'utf-8',
            'sort': 0,
            'num': 20,
            'repllyunm': 100,
            'cgi_host': 'http://taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6',
            'callback': '_preloadCallback',
            'code_version': 1,
            'format': 'jsonp',
            'need_private_comment': 1,
            'g_tk': self.g_tk
        }
        url = url + parse.urlencode(params)
        t = True
        pos = 0
        while t:
            url_ = url + '&pos=' + str(pos)
            mood = self.req.get(url_, headers=self.headers)
            if '\"msglist\":null' in mood.text:
                t = False
            else:
                tids = re.findall('"tid":".*?"', mood.text)
                for tid in tids:
                    print(tid.replace('"tid":', '').replace('"', ''))
                    self.tids.append(tid.replace('"tid":', '').replace('"', ''))
                pos += 20

    def del_mood(self):
        for tid in self.tids:
            print(tid)
            url = 'https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_delete_v6?' + \
                  '&g_tk=' + str(self.g_tk)
            data = {
                'hostuin': self.__username,
                'tid': tid,
                't1_source': 1,
                'code_version': 1,
                'format': 'fs',
                'qzreferrer': 'https://user.qzone.qq.com/' + self.__username
            }
            response = self.req.post(url, data=data, headers=self.headers).text
            if '"err":{"code":0}' in response:
                print('删除成功，继续删除中...')
            else:
                print('出现错误')


if __name__ == '__main__':
    sp = Spider()
    sp.login()
    sp.del_mood()
