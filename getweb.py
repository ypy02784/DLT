



import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pandas as pd
import time, datetime
pd.set_option('display.max_rows', None)

cn = create_engine('sqlite:///dlt.db')#便于同步github，先放d:盘
#按期数查
start_phase = '2007001'
end_phase = '2019028'
# https://chart.cp.360.cn/kaijiang/slt/?lotId=120029&chartType=undefined&spanType=3&span=2007001_2019028&r=0.7504661856439394#roll_0'


_START_DATE = '2007-05-01'
_NOWTIME = time.strftime('%Y-%m-%d', time.localtime(time.time()))  #默认系统当前日期
#https://chart.cp.360.cn/kaijiang/slt/?lotId=120029&chartType=undefined&spanType=2&span=2019-03-01_2019-03-14&r=0.2729831739188433#roll_132


def _url_date(starttime = _START_DATE):#根据日期创建查url
    url = 'https://chart.cp.360.cn/kaijiang/slt/?lotId=120029&chartType=undefined&spanType=2&span='+starttime+'_'+_NOWTIME+'&r=0.2729831739188433#roll_132'
    return url


def _url_phase(startphase=start_phase,endphase = end_phase):#根据期数创建url
    url = 'https://chart.cp.360.cn/kaijiang/slt/?lotId=120029&chartType=undefined&spanType=3&span=' + startphase + '_' + endphase + '&r=0.7504661856439394#roll_0'
    return url


def _get_html(urls):
    response = requests.get(urls)
    if response.status_code == 200:#有数据则返回的为200
        return response.text
    else:
        print('无数据！')
    return None


def _to_sqlite(html): #将数据存入sqlite数据库

    bf = BeautifulSoup(html, "html.parser")
    s = bf.find_all("tr")  # 返回的是tr列表

    a = []
    for u in range(4, len(s)):#从第4行开始，因为前三行为标题
        i = s[u].contents
        df = [i[0].text, i[1].text[0:10]]
        s1 = i[2].text.split('\xa0')
        df.append(s1[0])
        df.append(s1[1])
        df.append(s1[2])
        df.append(s1[3])
        df.append(s1[4])
        s2 = i[3].text.split('\xa0')
        df.append(s2[0])#篮球1
        df.append(s2[1])#篮球2
        df.append(i[4].text)#当期卖出总价
        df.append(i[5].text)#1等注数
        df.append(i[6].text)#1等奖金
        df.append(i[9].text)#奖池总数
        a.append(df)
    print(a)
    ssqdf = pd.DataFrame(a, columns=['phasenum', 'date', 'red1', 'red2', 'red3', 'red4', 'red5', 'blue1', 'blue2', 'jackpot', 'firstnum', 'firstprice', 'totalbet'])

    ssqdf.to_sql('dlt', con=cn, if_exists='append', index=False)
    print('添加'+str(len(a))+'期数据')


#获取表中最大日期,否则返回默认_STARTTIME
def _getMaxdateFromTable(tablename):
    sql = 'select max(date) from ' + tablename

    session = sessionmaker(cn)()
    result = session.execute(sql)
    result = result.fetchall()
    if result[0][0] is None:
        maxdate = _START_DATE
    else:
         maxdate = result[0][0]
    return _date_add1day(maxdate)


def _date_add1day(maxdate):
    a = datetime.datetime.strptime(maxdate,'%Y-%m-%d')
    a = a + datetime.timedelta(days=1)
    return (a.date())

_to_sqlite(_get_html(_url_date(str(_getMaxdateFromTable('dlt')))))


