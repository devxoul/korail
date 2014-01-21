# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup


class Schedule(object):
    src_station = None
    src_time = None
    dest_station = None
    dest_time = None
    first_class = False
    general_admission = False

    def __repr__(self):
        return '%s~%s(%s~%s) [특실:%d][일반실:%d]' % (
            self.src_station.encode('utf-8'),
            self.dest_station.encode('utf-8'),
            self.src_time.encode('utf-8'),
            self.dest_time.encode('utf-8'),
            self.first_class,
            self.general_admission,
        )


def euckr(s):
    return unicode(s, 'utf-8').encode('euc_kr')


def search(src, dest, date, time='000000'):
    """
    src -- 서울
    dest -- 부산
    date -- yyyyMMdd
    time -- hhmmss
    """
    url = 'http://www.korail.com/servlets/pr.pr21100.sw_pr21111_i1Svt'
    params = {
        'txtGoAbrdDt': date,
        'txtGoHour': time,
        'txtGoStart': euckr(src),
        'txtGoEnd': euckr(dest),
        'checkStnNm': 'Y',
        'radJobId': '1',  # 직통
    }
    r = requests.get(url, params=params)
    html = BeautifulSoup(r.text)
    error = html.select('.point02')
    if error:
        print error[0].string.strip()
        return

    schedules = []

    rows = html.select('table.list-view tr')
    for row in rows[1:]:
        schedule = Schedule()

        # 출발, 도착
        td11s = row.select('td[width=11%]')

        # 출발지, 출발시간
        src_td_contents = td11s[0].contents
        schedule.src_station = src_td_contents[0].strip()
        schedule.src_time = src_td_contents[1].contents[0].strip()

        # 도착지, 도착시간
        dest_td_contents = td11s[1].contents
        schedule.dest_station = dest_td_contents[0].strip()
        schedule.dest_time = dest_td_contents[1].contents[0].strip()

        # 특실, 일반실
        td7s = row.select('td[width=7%]')

        # 특실
        img = td7s[0].select('img')
        content = img[0] if img else td7s[0].contents[0]
        schedule.first_class = 'yes' in content.__str__()

        # 일반실
        img = td7s[1].select('img')
        content = img[0] if img else td7s[0].contents[0]
        schedule.general_admission = 'yes' in content.__str__()

        schedules.append(schedule)

    return schedules

search('서울', '동대구', '20140124', '100000')
