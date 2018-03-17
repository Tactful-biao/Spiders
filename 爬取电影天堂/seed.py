import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool

def get_seed(i):
    url = 'http://www.btbtdy.com/downlist/' + str(i) + '-0-0.html'
    headers = {
        'Host': 'www.btbtdy.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
    }
    try:
        html = requests.get(url, headers=headers).text
        soup = BeautifulSoup(html, 'lxml')
        title = soup.find_all('p')[0].getText()
        link = soup.find_all('p')[1].getText()
        data = {
            '电影名称:': title,
            '种子链接:': link
        }
        print(data)
        with open('seed.txt', 'a+', encoding='utf-8') as sd:
            sd.write(str(data) + '\n')
    except:
        with open('error.txt', 'a+', encoding='utf-8') as e:
            e.write('遇到异常，链接的id是: ' + str(i) + '\n')
        pass

if __name__ == '__main__':
    pool = Pool(10)
    page = [x for x in range(1, 12411)]
    pool.map(get_seed, page)
    pool.close()
    pool.join()

