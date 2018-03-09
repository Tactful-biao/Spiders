import requests
import time
from bs4 import BeautifulSoup
from PIL import Image

class Ncre:
    def __init__(self):
        self.s = requests.Session()
        self.cookies = 'UM_distinctid=1614f479c3a22a-0dd2eec3aee588-3976045e-1fa400-1614f479c3b75c;' \
                       'Hm_lvt_dc1d69ab90346d48ee02f18510292577=1517811704,1517811710,1517811930,1517812637;' \
                       'language=1;' \
                       'Hm_lpvt_dc1d69ab90346d48ee02f18510292577='+str(int(time.time()))+';'
        self.headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729)',
            'Host': 'search.neea.edu.cn',
            'Referer': 'http://search.neea.edu.cn/QueryMarkUpAction.do?act=doQueryCond&pram=results&community=Home&sid=300',
        }
        self.get_yzm()
        self.get_date()

    def get_yzm(self):
        url = 'http://search.neea.edu.cn/Imgs.do?act=verify&amp;t=0.8841180045674784'
        yz = self.s.get(url, headers=self.headers).content
        with open('yzm.jpg', 'wb+') as jpg:
            jpg.write(yz)
        ck = self.s.cookies.get_dict()
        for key, value in zip(ck.keys(), ck.values()):
            self.cookies += key + "=" + value + ';'
        with open('cookies', 'w') as ck:
            ck.write(self.cookies)
        im = Image.open('yzm.jpg')
        im.show()

    def get_date(self):
        with open('cookies', 'r') as ck:
            cookie = ck.read()
        yzm = input("输入验证码:")
        url_ = 'http://search.neea.edu.cn/QueryMarkUpAction.do?act=doQueryResults'
        params = {  # 针对不同的查询，需要改的地方有nexturl的ksnf参数和bkjb
            'pram': 'results',
            'ksxm': 300,
            'sf': '',
            'zkzh': '',
            'nexturl': '/QueryMarkUpAction.do?act=doQueryCond&sid=300&pram=results&ksnf=3aEEoPlhFcgFDWD9AVqX47D&sf=&bkjb=65&sfzh=' + ID + '&name='+name,
            'ksnf': '3aEEoPlhFcgFDWD9AVqX47D',
            'bkjb': 65,
            'sfzh': ID,
            'name': name,
            'verify': yzm
        }
        self.headers['Content-Length'] = '336'
        self.headers['Cache-Control'] = 'max-age=0'
        self.headers['Upgrade-Insecure-Requests'] = '1'
        self.headers['Cookie'] = cookie
        html = requests.post(url_, data=params, headers=self.headers).text
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find('table', attrs={'class': 'imgtab'})
        td = table.findAll('td')
        for i in td:
            print(i.getText().strip())

if __name__ == '__main__':
    ID = input('请输入身份证号: ')  
    name = input('请输入姓名: ') 
    try:
        nc = Ncre()
    except:
        print('请仔细检查输入数据是否正确!并重新输入')
        nc = Ncre()
