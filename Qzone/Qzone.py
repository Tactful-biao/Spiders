from selenium import webdriver
import time
import json
import random
import requests
from urllib import parse
import qq_init as qq
import pymongo


class Spider(object):
    def __init__(self):
        self.driver = webdriver.PhantomJS()
        self.driver.get('http://user.qzone.qq.com/')
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
        self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.db = self.client['QQ']

    def login(self):
        self.driver.switch_to.frame('login_frame')
        self.driver.find_element_by_id('switcher_plogin').click()
        self.driver.find_element_by_id('u').clear()
        self.driver.find_element_by_id('u').send_keys(self.__username)
        self.driver.find_element_by_id('p').clear()
        self.driver.find_element_by_id('p').send_keys(self.__password)
        self.driver.find_element_by_id('login_button').click()
        time.sleep(3)
        self.driver.implicitly_wait(3)
        self.driver.get('http://user.qzone.qq.com/{}'.format(self.__username))
        cookie = ''
        for item in self.driver.get_cookies():
            cookie += item["name"] + '=' + item['value'] + ';'
        self.cookies = cookie
        self.get_g_tk()
        self.headers['Cookie'] = self.cookies
        self.get_friends()
        self.driver.quit()


    def get_friends_url(self):
        url = 'https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/right/get_entryuinlist.cgi?'
        params = {
            'uin': self.__username,
            'ver': 1,
            'fupdate': 1,
            'action': 1,
            'g_tk': self.g_tk
        }
        url = url + parse.urlencode(params)
        return url

    def get_friends(self):
        offset = 0
        t = True
        url = self.get_friends_url()
        friends_list = []
        name = []
        qq_num = []
        while (t):
            url_ = url + '&offset=' + str(offset)
            page = self.req.get(url=url_, headers=self.headers)
            if '\"end\":1' in page.text:
                t = False
            else:
                data = page.text[95:-5]
                a = json.loads(data)
                for j in a:
                    friends_list.append(j)
                offset += 50
        for ii in range(len(friends_list)):
            name.append(friends_list[ii]['label'])
            qq_num.append(friends_list[ii]['data'])
        self.name = name
        self.qq_num = qq_num

    def get_g_tk(self):
        p_skey = self.cookies[self.cookies.find('p_skey=') + 7: self.cookies.find(';', self.cookies.find('p_skey='))]
        h = 5381
        for i in p_skey:
            h += (h << 5) + ord(i)
        print('g_tk', h & 2147483647)
        self.g_tk = h & 2147483647

    def get_mood(self):
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
            t1 = True
            url_ = url + '&uin=' + str(q)
            pos = 0
            black = self.db['black']
            shuoshuo = self.db['shuoshuo']
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
                        print(data)
                        black.insert(data)
                else:
                    shuo = mood.text[17: -2]
                    try:
                        js = json.loads(shuo)
                        for s in js['msglist']:
                            unikey = []
                            if not s['commentlist']:
                                s['commentlist'] = list()
                            if 'pic' in s:
                                pics = []
                                for j in range(len(s['pic'])):
                                    pics.append(s['pic'][j]['url2'])
                                if len(s['pic']) == 1:
                                    unikey.append(s['pic'][0]['curlikekey'])
                            else:
                                pics = []
                                unikey.append('http://user.qzone.qq.com/{}/mood/'.format(q) + s['tid'] + '.1')
                            like_url = 'https://user.qzone.qq.com/proxy/domain/users.qzone.qq.com/cgi-bin/likes/get_like_list_app?'
                            if len(unikey) is not 0:
                                param = {
                                    'uin': self.__username,
                                    'unikey': unikey[0],
                                    'begin_uin': 0,
                                    'query_count': 60,
                                    'if_first_page': 1,
                                    'g_tk': self.g_tk
                                }
                                like_url = like_url + parse.urlencode(param)
                                like = self.req.get(url=like_url, headers=self.headers)
                                m = like.text.encode(like.encoding)
                                p = m.decode('utf-8')
                                li = json.loads(p[10: -3])
                                likers = []
                                if len(li['data']['like_uin_info']) is not 0:
                                    for lik in range(len(li['data']['like_uin_info'])):
                                        info = {
                                            'fuin': li['data']['like_uin_info'][lik]['fuin'],
                                            'sex': li['data']['like_uin_info'][lik]['gender'],
                                            'nick': li['data']['like_uin_info'][lik]['nick'],
                                            'address': li['data']['like_uin_info'][lik]['addr'],
                                            'constellation': li['data']['like_uin_info'][lik]['constellation']
                                        }
                                        likers.append(info)
                                data = {
                                    'name': str(s['name']),
                                    '_id': str(s['uin']) + '_' + str(random.random() * 10).replace('.', ''),
                                    'CreateTime': time.strftime('%Y-%m-%d %H:%M:%S',
                                                                time.localtime(int(s['created_time']))),
                                    'source': s['source_name'],
                                    'content': s['content'],
                                    'forward': int(s['fwdnum']),
                                    'comment_content': str(
                                        [(x['content'], x['createTime2'], x['name'], x['uin']) for x in
                                         list(s['commentlist'])]),
                                    'comment': int(s['cmtnum']),
                                    'pic': pics,
                                    'like': li['data']['total_number'],
                                    'likers': likers
                                }
                                if shuoshuo.insert(data):
                                    print('%s 的说说写入到数据库成功！' % self.name[self.qq_num.index(q)])
                        pos += 20
			time.sleep(3)
                    except:
                        print('%s 的说说写入到数据库失败！' % self.name[self.qq_num.index(q)])

    def get_board(self):
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
                    try:
                        b = json.loads(board.text[75:-4])
                        da = b['commentList']
                        total = b['total']
                        for i in range(len(da)):
                            detail = da[i]
                            if detail['replyList'] is '[]':
                                data = {
                                    '_id': str(detail['uin']) + '_' + str(detail['id']),
                                    'owner': self.name[self.qq_num.index(q)],
                                    'total': total,
                                    'name': detail['nickname'],
                                    'qq': detail['uin'],
                                    'time': detail['pubtime'],
                                    'content': detail['ubbContent'],
                                    'replyList': []
                                }
                                if boardb.insert(data):
                                    print('%s 的留言存储到Mongodb成功！' % self.name[self.qq_num.index(q)])
                            else:
                                content = []
                                for ii in range(len(detail['replyList'])):
                                    content.append(
                                        detail['replyList'][ii]['nick'] + ':' + detail['replyList'][ii]['content'])
                                data = {
                                    '_id': str(detail['uin']) + '_' + str(detail['id']),
                                    'owner': self.name[self.qq_num.index(q)],
                                    'total': total,
                                    'name': detail['nickname'],
                                    'qq': detail['uin'],
                                    'time': detail['pubtime'],
                                    'content': detail['ubbContent'],
                                    'replyList': content
                                }
                                if boardb.insert(data):
                                    print('%s 的留言存储到Mongodb成功！' % self.name[self.qq_num.index(q)])
                    except:
                        print('%s 的留言存储到Mongodb失败！！' % self.name[self.qq_num.index(q)])
                    start += 10

    def get_information(self):
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
                    s = info.text[79: -4]
                    try:
                        w = json.loads(s)
                        sex = ['其他', '男', '女']
                        marriage = ['未填写', '单身', '已婚', '保密']
                        constellation = ['白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座', '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座', '未填写']
                        if w['constellation'] is -1:
                            w['constellation'] = 12
                        data = {
                            '_id': str(w['uin']) + '_' + str(random.random() * 10).replace('.', ''),
                            'nickname': w['nickname'],
                            'spacename': w['spacename'],
                            'desc': w['desc'],
                            'signature': w['signature'],
                            'sex': sex[w['sex']],
                            'age': w['age'],
                            'birthday': str(w['birthyear']) + '-' + str(w['birthday']),
                            'constellation': constellation[w['constellation']],
                            'country': w['country'],
                            'province': w['province'],
                            'city': w['city'],
                            'hometown': w['hco'] + w['hp'] + w['hc'],
                            'marriage': marriage[w['marriage']],
                            'career': w['career'],
                            'address': w['cb'],
                        }
                        if table.insert(data):
                            print('%s 的信息写入到数据库成功！' % self.name[self.qq_num.index(q)])
                    except:
                        print('%s的个人信息数据统计出错！' % self.name[self.qq_num.index(q)])
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
