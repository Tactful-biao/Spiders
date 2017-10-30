import requests
import stations
import time
import info
from monior import sentmail
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_tickets(appoin=None):
    while(True):
        train_date = info.train_date
        start = info.start
        stop = info.stop
        from_station = stations.get_telecode(start)
        to_station = stations.get_telecode(stop)
        url = (
            'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.'
            'train_date={}&'
            'leftTicketDTO.from_station={}&'
            'leftTicketDTO.to_station={}&'
            'purpose_codes=ADULT'
        ).format(train_date, from_station, to_station)
        headers = {
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        data = requests.get(url, headers=headers, verify=False).json()
        result = data['data']['result']
        lenth = len(result)
        trains = []
        hard_sleeper = []
        hard_seat = []
        first_class_seat = []
        second_class_seat = []
        gord = []
        for i in range(int(lenth)):
            x = result[i].split('|')
            gord.append(x[3][0])
            trains.append(x[3])
            hard_seat.append(x[29])
            hard_sleeper.append(x[28])
            first_class_seat.append(x[31])
            second_class_seat.append(x[30])
        try:
            appoint = trains.index(appoin)
            if (gord[appoint] == 'G' or gord == 'D'):
                one = (first_class_seat[appoint] != '无' and first_class_seat[appoint] != ' ')
                two = (second_class_seat[appoint] != '无' and second_class_seat[appoint] != ' ')
                while (one or two):
                    if (one):
                        sentmail(('始发站:%s' + '\n' + '终点站:%s' + '\n' + '时间:%s' + '\n' + '车次:%s' + '\n' + '该列车有一等座票！')
                                % (start, stop, train_date, trains[appoint]), '火车票监票脚本', 3600)
                    else:
                        sentmail(('始发站:%s' + '\n' + '终点站:%s' + '\n' + '时间:%s' + '\n' + '车次:%s' + '\n' + '该列车有二等座票！')
                                % (start, stop, train_date, trains[appoint]), '火车票监票脚本', 3600)
            else:
                three = (hard_sleeper[appoint] != '无' and hard_sleeper[appoint] != ' ')
                four = (hard_seat[appoint] != '无' and hard_seat[appoint] != ' ')
                while (three or four):
                    if (three):
                        sentmail(('始发站:%s' + '\n' + '终点站:%s' + '\n' + '时间:%s' + '\n' + '车次:%s' + '\n' + '该列车有卧铺票！')
                                % (start, stop, train_date, trains[appoint]), '火车票监票脚本', 3600)
                    else:
                        sentmail(('始发站:%s' + '\n' + '终点站:%s' + '\n' + '时间:%s' + '\n' + '车次:%s' + '\n' + '该列车有硬座票！')
                                % (start, stop, train_date, trains[appoint]), '火车票监票脚本', 3600)
        except ValueError:
            for j in range(int(lenth)):
                if (gord[j] == 'G' or gord == 'D'):
                    one = (first_class_seat[j] != '无' and first_class_seat[j] != ' ')
                    two = (second_class_seat[j] != '无' and second_class_seat[j] != ' ')
                    while (one or two):
                        if (one):
                            sentmail(('始发站:%s' + '\n' + '终点站:%s' + '\n' + '时间:%s' + '\n' + '车次:%s' + '\n' + '该列车有一等座票！')
                                % (start, stop, train_date, trains[j]), '火车票监票脚本', 3600)
                        else:
                            sentmail(('始发站:%s' + '\n' + '终点站:%s' + '\n' + '时间:%s' + '\n' + '车次:%s' + '\n' + '该列车有二等座票！')
                                % (start, stop, train_date, trains[j]), '火车票监票脚本', 3600)
                else:
                    three = (hard_sleeper[j] != '无' and hard_sleeper[j] != ' ')
                    four = (hard_seat[j] != '无' and hard_seat[j] != ' ')
                    while (three or four):
                        if (three):
                            sentmail(('始发站:%s' + '\n' + '终点站:%s' + '\n' + '时间:%s' + '\n' + '车次:%s' + '\n' + '该列车有卧铺票！')
                                % (start, stop, train_date, trains[j]), '火车票监票脚本', 3600)
                        else:
                            sentmail(('始发站:%s' + '\n' + '终点站:%s' + '\n' + '时间:%s' + '\n' + '车次:%s' + '\n' + '该列车有硬座票！')
                                % (start, stop, train_date, trains[j]), '火车票监票脚本', 3600)
        time.sleep(3)

if __name__ == '__main__':
    get_tickets(info.appoin)