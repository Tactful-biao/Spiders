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
        self.__username = qq.qq1
        self.__password = qq.mm1
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
        self.driver.switch_to.frame('login_frame')
        self.driver.find_element_by_id('switcher_plogin').click()
        self.driver.find_element_by_id('u').clear()
        self.driver.find_element_by_id('u').send_keys(self.__username)
        self.driver.find_element_by_id('p').clear()
        self.driver.find_element_by_id('p').send_keys(self.__password)
        self.driver.find_element_by_id('login_button').click()
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
        url = 'https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/friend_hat_get.cgi?'
        params = {
            'uin': self.__username,
            'fupdate': 1,
            'g_tk': self.g_tk
        }
        url = url + parse.urlencode(params)
        friends = self.req.get(url, headers=self.headers).text
        name, qq_num = [], []
        for _qq, _name in zip(re.findall('"\d+"', friends), re.findall('"realname":.*"', friends)):
            name.append(re.sub('"|realname|:', '', _name))
            qq_num.append(re.sub('"', '', _qq))
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
                    created_time = re.findall('created_time":\d+', mood.text)
                    source = re.findall('source_appid":".*?"source_name":".*?"', mood.text)
                    contents = re.findall('],"content":".*?"', mood.text)
                    forword = re.findall('fwdnum":\d+', mood.text)
                    comment_content = re.findall('commentlist":(null|.*?],)', mood.text)
                    comments = re.findall('cmtnum":\d+', mood.text)
                    pics = re.findall('","pic(_template|".*?])', mood.text)
                    like_url = 'https://user.qzone.qq.com/proxy/domain/users.qzone.qq.com/cgi-bin/likes/get_like_list_app?'
                    tids = re.findall('tid":".*?"', mood.text)

                    for _time, _source, _content, _forword, _comment_content, _comment, _pic, _tid in \
                            zip(created_time, source, contents, forword, comment_content, comments, pics, tids):
                        param = {
                            'uin': self.__username,
                            'unikey': 'http://user.qzone.qq.com/{}/mood/'.format(q)+re.sub('tid":"|"', '', _tid)+'.1',
                            'begin_uin': 0,
                            'query_count': 60,
                            'if_first_page': 1,
                            'g_tk': self.g_tk
                        }
                        like_url = like_url + parse.urlencode(param)
                        like = self.req.get(url=like_url, headers=self.headers)
                        likers = like.text.encode(like.encoding).decode('utf-8')
                        fuin, nick, sex, constellation, address = re.findall('fuin":\d+', likers), re.findall('nick":".*?"', likers), re.findall('gender":".*?"', likers), re.findall('tion":".*?"', likers), re.findall('addr":".*?"', likers)
                        infos = []
                        for _fuin, _nick, _sex, _constellation, _address in zip(fuin, nick, sex, constellation, address):
                            info = {
                                'fuin': re.sub('fuin":', '', _fuin),
                                'nick': re.sub('nick":"|"', '', _nick),
                                'sex': re.sub('gender":"|"', '', _sex),
                                'constellation': re.sub('tion":"|"', '', _constellation),
                                'address': re.sub('addr":"|"', '', _address)
                            }
                            infos.append(info)
                        data = {
                            '_id': str(q) + '_' + str(random.random() * 10).replace('.', ''),
                            'name': self.name[self.qq_num.index(q)],
                            'CreateTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(re.sub('created_time":', '', _time)))),
                            'source': re.sub('source_appid":".*?"source_name":"|"', '', _source),
                            'content': re.sub('],"content":"|"', '', _content),
                            'forward': re.sub('fwdnum":', '', _forword),
                            'comment_content': re.sub('null|commentlist":', '', _comment_content) if 'null' in _comment_content else str([(re.sub('content":"|"', '', x), re.sub('createTime2":"|"', '', y), re.sub('name":"|"', '', z), re.sub('uin":', '', zz)) for x, y, z, zz in zip(re.findall('content":".*?"', _comment_content), re.findall('createTime2":".*?"', _comment_content), re.findall('name":".*?"', _comment_content), re.findall('uin":\d+', _comment_content))]),
                            'comment': re.sub('cmtnum":', '', _comment),
                            'pic': [] if 'template' in _pic else [re.sub('url2":|"', '', i) for i in re.findall('url2":".*?"', _pic)],
                            'like': re.sub('number":', '', re.search('number":\d+', likers).group()),
                            'likers': infos
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
                        re.findall('id":"\d+', text), re.findall('nickname":".*?"', text), re.findall('uin":\d+,\n"nick', text),\
                        re.findall('pubtime":".*?"', text), re.findall('ubbContent":".*?"', text), re.findall('"replyList":(\[\]|.*?\}\])', text, re.S)
                    for _id, _nickname, _uin, _time, _content, _reply in zip(ids, nickname, uin, pubtime, content, replyList):
                        data = {
                            '_id': str(q) + '_' + re.sub('id":"', '', _id),
                            'owner': self.name[self.qq_num.index(q)],
                            'total': re.sub('total":', '', re.search('total":\d+', board.text).group()),
                            'name': re.sub('nickname":"|"', '', _nickname),
                            'qq': re.sub('uin":|,\n"nick', '', _uin),
                            'time': re.sub('pubtime":"|"', '', _time),
                            'content': re.sub('ubbContent":"|"', '', _content),  # 下行需要改动
                            'replyList': [] if '[]' in _reply else str([re.sub('nick":"|"', '', name) + re.sub('content"|"', '', con) for name, con in zip(re.findall('nick":".*?"', _reply), re.findall('content":".*?"', _reply))])
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
                        'nickname': re.sub('nickname":"|"', '', re.search('nickname":".*?"', text).group()),
                        'spacename': re.sub('spacename":"|"', '', re.search('spacename":".*?"', text).group()),
                        'desc': re.sub('desc":"|"', '', re.search('desc":".*?"', text).group()),
                        'signature': re.sub('signature":"|"', '', re.search('signature":".*?"', text).group()),
                        'sex': sex[int(re.sub('sex":', '', re.search('sex":\d+', text).group()))],
                        'age': re.sub('"age":', '', re.search('"age":\d+', text).group()),
                        'birthday': re.sub('birthyear":', '', re.search('birthyear":\d+', text).group()) + '-' + re.sub('birthday":"|"', '', re.search('birthday":".*"', text).group()),
                        'constellation': constellation[int(re.sub('constellation":|,', '', re.search('constellation":.*,', text).group()).replace('-1', '12'))],
                        'country': re.sub('country":"|"', '', re.search('country":".*"', text).group()),
                        'province': re.sub('province":"|"', '', re.search('province":".*?"', text).group()),
                        'city': re.sub('city":"|"', '', re.search('city":".*?"', text).group()),
                        'hometown': re.sub('hco":"|"|,|\n|hc|hp|:', '', re.search('hco":".*\n".*\n".*', text).group()),
                        'marriage': marriage[int(re.sub('marriage":', '', re.search('marriage":\d', text).group()))],
                        'career': re.sub('career":"|"', '', re.search('career":".*?"', text).group()),
                        'address': re.sub('cb":"|"', '', re.search('cb":".*?"', text).group())
                    }
                    if table.insert(data):
                        print('%s 的信息写入到数据库成功！' % self.name[self.qq_num.index(q)])
                    t3 = False

if __name__ == '__main__':
    sp = Spider()
    sp.login()
    sp.get_information()
    t = time.perf_counter()
    sp.get_board()
    sp.get_mood()
    End = time.perf_counter() - t
    print('所有内容爬取完成！总用时%s!' % End)
