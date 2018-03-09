import requests
from PIL import Image
from bs4 import BeautifulSoup
from urllib import parse

class CET:
    def __init__(self):
        ''' 初始化 '''
        self.s = requests.session()
        self.cookies = '__utmt=1; ' \
         '__utma=65168252.468897637.1517456114.1517456114.1520232128.2; ' \
         '__utmb=65168252.7.10.1520232128; ' \
         '__utmc=65168252; ' \
         '__utmz=65168252.1517456114.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); '

        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'keep-alive',
            'Host': 'www.chsi.com.cn',
            'Referer': 'http://www.chsi.com.cn/cet/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'
        }
        self.get_yzm()
        self.get_data()

    def get_yzm(self):
        '''
        获取验证码，把验证码和cookies保存到本地
        '''
        yzm_url = 'http://www.chsi.com.cn/cet/ValidatorIMG.JPG?ID=3677.4286808430857'
        yz = self.s.get(yzm_url, headers=self.headers).content
        with open('yzm.jpg', 'wb+') as jpg:
            jpg.write(yz)
        ck = self.s.cookies.get_dict()
        for key, value in zip(ck.keys(), ck.values()):
            self.cookies += key + "=" + value + ';'
        with open('cookies', 'w') as ck:
            ck.write(self.cookies)
        im = Image.open('yzm.jpg')
        im.show()

    def get_data(self):
        '''
        获取数据
        从本地读取cookies
        '''
        datas = []
        with open('cookies', 'r') as ck:
            cookie = ck.read()
        yzm = input("输入验证码:")
        url_ = 'http://www.chsi.com.cn/cet/query?'
        params = {
            'zkzh': num,
            'xm': name,
            'yzm': yzm
        }
        self.headers['Cookie'] = cookie
        url = url_ + parse.urlencode(params)
        html = requests.get(url, headers=self.headers).text
        '''提取数据'''
        soup = BeautifulSoup(html, 'lxml')
        content = soup.find('div', attrs={'class': 'm_cnt_m'})
        if content.find('div', attrs={'class': 'error alignC'}):
            print('验证码不正确')

        elif content.find('div', attrs={'class': 'error alignC marginT20'}):
            print('无法找到对应的分数，请确认您输入的准考证号及姓名无误。')

        else:
            result_item = content.findAll("td")
            for i in result_item:
                datas.append(i.getText())

            print('姓   名: ' + datas[0].strip())
            print('学   校: ' + datas[1].strip())
            print('考试级别: ' + datas[2].strip())
            print('\n\t\t笔 试 成 绩\t\t\n')
            print('准考证号: ' + datas[3].strip())
            print('总    分: ' + datas[4].strip())
            print('\t\t听     力: ' + datas[6].strip())
            print('\t\t阅     读: ' + datas[8].strip())
            print('\t\t写作和翻译: ' + datas[10].strip())
            print('\n\t\t口 语 成 绩\t\t\n')
            print('准考证号: ' + datas[11].strip())
            print('等   级: ' + datas[12].replace('\r\n ', ''))

if __name__ == '__main__':
    name = input('请输入姓名: ')
    num = input('请输入准考证号: ')
    cet = CET()
