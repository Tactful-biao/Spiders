import requests
import re

start_url = 'http://spys.one/en/free-proxy-list/'
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Host': 'spys.one',
    'Origin': 'http://spys.one',
    'Referer': 'http://spys.one/en/free-proxy-list/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
 }

data = {
    'xpp': '5',
    'xf1': '0',
    'xf2': '0',
    'xf4': '0',
    'xf5': '1'
}

html = requests.post(start_url, data=data, headers=headers).text
text = re.sub('=\d\^\w{4}', '', re.sub('javascript">', '', re.search('javascript">\w{4}=\d+.*;',html).group(0)))
ips = re.findall('\d+\.\d+\.\d+\.\d+', html)
base = text.split(';')[-11:-1]
ports = re.findall('\(\w+\^\w{4}\S+\)', html)

for ip, port in zip(ips, ports):
    aa = re.sub('\^\w{4}', '', port).replace('(', '').replace(')', '').split('+')
    for i in range(len(aa)):
        aa[i] = base.index(aa[i])
    xs = [str(x) for x in aa]
    result = ip + ':' + ''.join(xs)
    print(result)
