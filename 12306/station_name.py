
import re
import requests

def main():
    url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9018'
    r = requests.get(url, verify=False)
    pattern = u'([\u4e00-\u9fa5]+)\|([A-Z]+)'
    stations = dict(re.findall(pattern, r.text))
    print(stations.keys())
    print(stations.values())


if __name__ == '__main__':
    main()