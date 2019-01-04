import requests
from Crypto.Cipher import AES
import base64
import re


def get_comments(ids):
    ‘’‘
    获取评论，正则提取
    ’‘’
    key = '0CoJUm6Qyw8W8jud'
    # 通过offset来控制翻页，每页增加20， total除第一页是true外，其他页均为false，limit最大为100
    text = '{rid: "", offset: "0", total: "true", limit: "100", csrf_token: ""}'
    url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_'+ids+'?csrf_token='
    headers = {
        'Cookie': 'JSESSIONID-WYYY=vDeNaw5OspW8kcNaX%5CsngVIwR3Z%2FigZ0HHGIb2duQgPm%2FFhGpQs6c26bKN3xf9tOatRbKk1JlTpJCiNsrZCsACk%2BN296WbpNc%2Fn96i8Ih6NYvHkjqXRR165SZAxv9YkkSAzfH9WTgCnyJUV6PEB9mm%2BJsduyy0B%5Cf2S7zXIdbls2hHY7%3A1519467798967; _iuqxldmzr_=32; _ntes_nnid=fc7bf97086aab1c7e5ea7559945fc3fe,1519465998987; _ntes_nuid=fc7bf97086aab1c7e5ea7559945fc3fe; __utma=94650624.1089055467.1519466000.1519466000.1519466000.1; __utmz=94650624.1519466000.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _ngd_tid=izuEtMCQO5AHgNjd7VBI%2FItSs427hfCz',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    # encSecKey 是通过把原链接js中的i(16位随机字符串)改成'biaobiaobiaobiao'获得的。
    params = {
        'params': str(get_params(key, text), 'utf-8'),
        'encSecKey': '48a9661615fa0502afdcd25020d2add36961a23e8fa5c6705c4e4b9620f2b338331405db1d6d73ffe498729c8f4f0f97d334f2f662ac02191dc81b7ea455ef0bce48c78c579082f0f6c02e6f386f6cb1f1c22c4240954855fa3dfa9929ae081932813743362b26c5de258e349e8d73ebcc9d6e78275cbd4bf872616ee1c283bb'
    }
    res = requests.post(url, headers=headers, data=params).text
    content = re.findall('"content":".*?"', res)
    for i in content:
        print(re.sub('"content":|"|\n', '', i))

def get_params(key, text):
    ’‘’
    通过aes加密获取params参数
    ‘’’
    h_enctext = aes_encrpt(key, text)
    # 其中‘biaobiaobiaobiao’是和上面的encSecKey是配套的，要改两部分都需要改，必须使用同一个16位随机字符串才可以。
    h_enctext = aes_encrpt('biaobiaobiaobiao', str(h_enctext, 'utf-8'))
    return h_enctext


def aes_encrpt(key, text):
    ‘’‘
    编写aes加密算法
    ’‘’
    iv = '0102030405060708'
    pad = 16 - len(text) % 16  # 加密长度要达到16位
    text +=  pad * chr(pad)    # 不够的在后面补充占位符
    encryptor = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    encrypt_text = encryptor.encrypt(text.encode('utf-8'))
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text

if __name__ == '__main__':
    ids = input('请输入歌曲的id')  # '574566207'
    get_comments(ids)
