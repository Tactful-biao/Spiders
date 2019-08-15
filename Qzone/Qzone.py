from selenium import webdriver
import time
import re
import random
import requests
from urllib import parse
import qq_init as qq
import pymongo

class Spider(object):
    def __init__(self):
        '''
        初始化
        '''
        self.driver = webdriver.PhantomJS()
        self.driver.get('https://qzone.qq.com/')
        self.__username = qq.qq
        self.__password = qq.mm
        self.headers = {
            'host': 'h5.qzone.qq.com',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.8',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'connection': 'keep-alive'
        }
        self.req = requests.Session()
        self.cookies = {}
        self.client = pymongo.MongoClient(host=qq.host, port=qq.port)
        self.db = self.client[qq.db]

    def login(self):
        '''
        登录、调用get_g_tk()、get_friends()函数
        :return:
        '''
        self.driver.set_window_position(20, 40)
        self.driver.set_window_size(1100, 700)
        self.driver.switch_to.frame('login_frame')
        self.driver.execute_script("var a = document.getElementById('qlogin_list');a.removeChild(a.firstElementChild);")
        self.driver.find_element_by_id('switcher_plogin').click()
        self.driver.find_element_by_id('u').clear()
        self.driver.find_element_by_id('u').send_keys(self.__username)
        time.sleep(2)
        self.driver.find_element_by_id('p').clear()
        self.driver.find_element_by_id('p').send_keys(self.__password)
        time.sleep(2)
        self.driver.find_element_by_id('login_button').click()
        time.sleep(3)
        self.driver.get('http://user.qzone.qq.com/{}'.format(self.__username))
        cookie = ''
        for item in self.driver.get_cookies():
            cookie += item["name"] + '=' + item['value'] + ';'
        self.cookies = cookie
        self.get_g_tk()
        self.headers['Cookie'] = self.cookies
        self.get_friends()
        self.driver.quit()

    def get_friends(self):
        '''
        获取全部好友
        :return: qq, name
        '''
        url = 'https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/right/get_entryuinlist.cgi?'
        params = {
            'uin': self.__username,
            'fupdate': 1,
            'action': 1,
            'g_tk': self.g_tk
        }
        _url = url + parse.urlencode(params)
        offset = 0
        name, qq_num = [], []
        while True:
            url = _url + '&offset=' + str(offset)
            friends = self.req.get(url, headers=self.headers).text
            if '\"end\":1' not in friends and '\"uinlist\":[]' not in friends:
                for _qq, _name in zip(re.findall('"data":"(\d+)"', friends), re.findall('"label":"(.*?)"', friends)):
                    name.append(_name)
                    qq_num.append(_qq)
            else:
                break
            offset += 50

        self.name, self.qq_num = name, qq_num

    def get_g_tk(self):
        '''
        获取g_tk()
        :return: 生成的g_tk
        '''
        p_skey = self.cookies[self.cookies.find('p_skey=') + 7: self.cookies.find(';', self.cookies.find('p_skey='))]
        h = 5381
        for i in p_skey:
            h += (h << 5) + ord(i)
        print('g_tk', h & 2147483647)
        self.g_tk = h & 2147483647

    def get_mood(self):
        '''
        构造说说请求链接
        对所有好友进行请求
        获取点赞好友信息
        正则解析
        存入数据库
        设置时长 5 秒，防封号
        :return:
        '''
        url = 'https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?'
        params = {
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
        for q in self.qq_num:
            t1, pos = True, 0
            url_ = url + '&uin=' + str(q)
            black, shuoshuo = self.db['black'], self.db['mood']
            while(t1):
                url__ = url_ + '&pos=' + str(pos)
                mood = self.req.get(url=url__, headers=self.headers)
                if '\"msglist\":null' in mood.text or "\"message\":\"对不起,主人设置了保密,您没有权限查看\"" in mood.text:
                    t1 = False
                    if '\"message\":\"对不起,主人设置了保密,您没有权限查看\"' in mood.text:
                        data = {
                            'name': self.name[self.qq_num.index(q)],
                            'qq': q
                        }
                        black.insert(data)
                else:
                    created_time = re.findall('created_time":(\d+)', mood.text)
                    source = re.findall('source_appid":".*?"source_name":"(.*?)"', mood.text)
                    contents = re.findall('],"content":"(.*?)"', mood.text)
                    forword = re.findall('fwdnum":(\d+)', mood.text)
                    comment_content = re.findall('commentlist":(null|.*?],)', mood.text)
                    comments = re.findall('cmtnum":(\d+)', mood.text)
                    pics = re.findall('","pic(_template|".*?])', mood.text)
                    tids = re.findall('tid":"(.*?)"', mood.text)

                    for _time, _source, _content, _forword, _comment_content, _comment, _pic, _tid in \
                            zip(created_time, source, contents, forword, comment_content, comments, pics, tids):
                        data = {
                            '_id': str(q) + '_' + str(random.random() * 10).replace('.', ''),
                            'name': self.name[self.qq_num.index(q)],
                            'CreateTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(_time))),
                            'source': _source,
                            'content': _content,
                            'forward': _forword,
                            'comment_content': re.sub('null|commentlist":', '', _comment_content) if 'null' in _comment_content else str([(x, y, z, zz) for x, y, z, zz in zip(re.findall('content":"(.*?)"', _comment_content), re.findall('createTime2":"(.*?)"', _comment_content), re.findall('name":"(.*?)"', _comment_content), re.findall('uin":(\d+)', _comment_content))]),
                            'comment': _comment,
                            'pic': [] if 'template' in _pic else [i for i in re.findall('url2":"(.*?)"', _pic)],
                        }

                        if shuoshuo.insert(data):
                            print('%s 的说说写入到数据库成功！' % self.name[self.qq_num.index(q)])
                        else:
                            with open('filed', 'a+', encoding='utf-8') as f:
                                f.write('%s 的说说爬取失败！\n' % self.name[self.qq_num.index(q)])
                            print('%s 的说说写入到数据库成功！' % self.name[self.qq_num.index(q)])
                    pos += 20
                    time.sleep(5)

    def get_board(self):
        '''
        获取留言， 与获取说说大同小异
        :return:
        '''
        url = 'https://user.qzone.qq.com/proxy/domain/m.qzone.qq.com/cgi-bin/new/get_msgb?'
        params = {
            'uin': self.__username,
            'num': 10,
            'hostword': 0,
            'essence': 1,
            'inCharset': 'utf-8',
            'outCharset': 'utf-8',
            'format': 'jsonp',
            'g_tk': self.g_tk
        }
        url = url + parse.urlencode(params)
        for q in self.qq_num:
            t2 = True
            url_ = url + '&hostUin=' + str(q)
            start = 0
            boardb = self.db['board']
            while(t2):
                url__ = url_ + '&start=' + str(start)
                board = self.req.get(url=url__, headers=self.headers)
                if '\"message":"空间主人设置了访问权限，您无法进行操作\"' in board.text or '\"message\":\"空间未开通\"' in board.text or '\"commentList\":[]' in board.text or '\"total\":0' in board.text:
                    t2 = False
                else:
                    text = board.text
                    ids, nickname, uin, pubtime, content, replyList = \
                        re.findall('id":"(\d+)', text), re.findall('nickname":"(.*?)"', text), re.findall('uin":(\d+),\n"nick', text),\
                        re.findall('pubtime":"(.*?)"', text), re.findall('ubbContent":"(.*?)"', text), re.findall('"replyList":(\[\]|.*?\}\])', text, re.S)
                    for _id, _nickname, _uin, _time, _content, _reply in zip(ids, nickname, uin, pubtime, content, replyList):
                        data = {
                            '_id': str(q) + '_' + _id,
                            'owner': self.name[self.qq_num.index(q)],
                            'total': re.search('total":(\d+)', board.text).group(1),
                            'name': _nickname,
                            'qq': _uin,
                            'time': _time,
                            'content': _content,  # 下行需要改动
                            'replyList': [] if '[]' in _reply else str([name + re.sub('\[em\]|e.*?\em\]', '', con) for name, con in zip(re.findall('nick":"(.*?)"', _reply), re.findall('content":"(.*?)"', _reply))])
                        }
                        if boardb.insert(data):
                            print('%s 的留言存储到Mongodb成功！' % self.name[self.qq_num.index(q)])
                    start += 10

    def get_information(self):
        '''
        构造请求，正则解析
        :return:
        '''
        url = 'https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/user/cgi_userinfo_get_all?'
        params = {
            'vuin': self.__username,
            'fupdate': 1,
            'g_tk': self.g_tk
        }
        url = url + parse.urlencode(params)
        table = self.db['information']
        for q in self.qq_num:
            t3 = True
            url_ = url + '&uin=' + str(q)
            while(t3):
                info = self.req.get(url=url_, headers=self.headers)
                if '\"message\":\"您无权访问\"' in info.text:
                    t3 = False
                else:
                    text = info.text
                    sex, marriage = ['其他', '男', '女'], ['未填写', '单身', '已婚', '保密', '恋爱中']
                    constellation = ['白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座', '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座', '未填写']
                    data = {
                        '_id': str(q) + '_' + str(random.random() * 10).replace('.', ''),
                        'nickname': re.search('nickname":"(.*?)"', text).group(1),
                        'spacename': re.search('spacename":"(.*?)"', text).group(1),
                        'desc': re.search('desc":"(.*?)"', text).group(1),
                        'signature': re.search('signature":"(.*?)"', text).group(1),
                        'sex': sex[int(re.search('sex":(\d+)', text).group(1))],
                        'age': re.search('"age":(\d+)', text).group(1),
                        'birthday': re.search('birthyear":(\d+)', text).group(1) + '-' + re.search('birthday":"(.*)"', text).group(1),
                        'constellation': constellation[int(re.search('constellation":(.*),', text).group(1).replace('-1', '12'))],
                        'country': re.search('country":"(.*)"', text).group(1),
                        'province': re.search('province":"(.*?)"', text).group(1),
                        'city': re.search('city":"(.*?)"', text).group(1),
                        'hometown': re.sub('hco":"|"|,|\n|hc|hp|:', '', re.search('hco":".*\n".*\n".*', text).group()),
                        'marriage': marriage[int(re.search('marriage":(\d)', text).group(1))],
                        'career': re.search('career":"(.*?)"', text).group(1),
                        'address': re.search('cb":"(.*?)"', text).group(1)
                    }
                    if table.insert(data):
                        print('%s 的信息写入到数据库成功！' % self.name[self.qq_num.index(q)])
                    t3 = False


if __name__ == '__main__':
    sp = Spider()
    sp.login()
    sp.get_information()
    sp.get_board()
    sp.get_mood()
    print('爬去完成')
