# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from datetime import datetime

session = requests.session()


class Train(object):
    #: 기차 종류
    train_type = None

    #: 출발역 코드
    dep_code = None

    #: 출발날짜 (yyyyMMdd)
    dep_date = None

    #: 출발시각 (hhmmss)
    dep_time = None

    #: 도착역 코드
    arr_code = None

    #: 도착 시각
    arr_time = None

    #: 인원
    count = 0

    #: 특실 예약가능 여부
    first_class = False

    #: 일반실 예약가능 여부
    general_admission = False

    def __repr__(self):
        return '[%s] %s~%s(%s~%s) [특실:%d][일반실:%d]' % (
            self.train_type.encode('utf-8'),
            self.dep_code.encode('utf-8'),
            self.dep_time.encode('utf-8'),
            self.arr_code.encode('utf-8'),
            self.arr_time.encode('utf-8'),
            self.first_class,
            self.general_admission,
        )


def all_stations():
    stations = []
    for i in range(14):
        url = 'http://www.korail.com/servlets/pr.pr11100.sw_pr11111_f1Svt'
        params = {
            'hidKorInx': i,
        }
        r = requests.get(url, params=params)
        html = r.text.split('<table class="s-view">')[3]
        rows = html.split("javascript:putStation('")[1:]
        for row in rows:
            name = row.split("'")[0]
            id = row.split(",'")[1].split("'")[0]
            stations.append((id, name))
    return stations


def login(id, password, use_phone=False):
    """
    :param id: 코레일 멤버십 번호 또는 휴대전화번호
    :param password: 비밀번호
    :param use_phone: 휴대전화번호 로그인 여부
    """
    url = 'https://www.korail.com/servlets/hc.hc14100.sw_hc14111_i2Svt'
    data = {
        'selInputFlg': '4' if use_phone else '2',  # 멤버십번호: 2, 휴대전화로그인: 4
        'UserId': id,
        'UserPwd': password,
        'hidMemberFlg': '1',  # 없으면 입력값 오류
    }
    r = session.post(url, data=data)
    if 'w_mem01106' in r.text:
        return True
    return False


def logout():
    url = 'http://www.korail.com/2007/mem/mem01000/w_mem01102.jsp'
    session.get(url)


def euckr(s):
    """
    문자열을 EUC-KR 유니코드로 변환하여 리턴한다.
    """
    return unicode(s, 'utf-8').encode('euc_kr')


def search(dep_code, arr_code, date, time='000000', train='05', count=1):
    """
    :param dep_code: 출발역 코드
    :param arr_code: 도착역 코드
    :param date: 날짜 (yyyyMMdd)
    :param time: 시간 (hhmmss)
    :param train: 기차 종류
                  - 00: KTX
                  - 01: 새마을호
                  - 02: 무궁화호
                  - 03: 통근열차
                  - 04: 누리로
                  - 05: 전체 (기본값)
                  - 06: 공학직통
                  - 09: ITX-청춘
    :param count: 인원
    """
    url = 'http://www.korail.com/servlets/pr.pr21100.sw_pr21111_i1Svt'
    params = {
        'txtGoAbrdDt': date,
        'txtGoHour': time,
        'txtGoStartCode': dep_code,
        'txtGoEndCode': arr_code,
        'checkStnNm': 'N',
        'radJobId': '1',  # 직통
        'txtPsgCnt1': count,
    }
    r = session.get(url, params=params)

    html = BeautifulSoup(r.text)
    error = html.select('.point02')
    if error:
        print error[0].string.strip()
        return

    rows = html.select('table.list-view tr')[1:]

    trains = []
    train_info = r.text.split('new train_info(')[1:]
    i = 0
    for info in train_info:
        obj = info.split(',')
        train = Train()
        train.train_type = obj[22].strip()[1:-1]
        train.dep_code = obj[18].strip()[1:-1]
        train.dep_date = obj[24].strip()[1:-1]
        train.dep_time = obj[25].strip()[1:-1]
        train.arr_code = obj[19].strip()[1:-1]
        train.arr_time = obj[27].strip()[1:-1]
        train.count = count

        td7s = rows[i].select('td[width=7%]')

        #특실
        img = td7s[0].select('img')
        content = img[0] if img else td7s[0].contents[0]
        train.first_class = 'yes' in content.__str__()

        #일반실
        img = td7s[1].select('img')
        content = img[0] if img else td7s[0].contents[0]
        train.general_admission = 'yes' in content.__str__()

        print train.first_class, train.general_admission
        trains.append(train)
        i += 1

    return trains


def reserve(train):
    """
    승차권 예약

    :param train: `Train` 인스턴스
    """
    session.headers = {
        'Referer': 'http://www.korail.com/servlets/pr.pr21100.sw_pr21111_i1Svt'
    }
    url = 'http://www.korail.com/servlets/pr.pr12100.sw_pr12111_i1Svt'
    data = {
        'txtCompaCnt1': train.count,  # 인원
        'txtDptRsStnCd1': train.dep_code,  # 출발역 코드
        'txtDptDt1': train.dep_date,  # 출발날짜
        'txtDptTm1': train.dep_time,  # 출발시각
        'txtArvRsStnCd1': train.arr_code,  # 도착역 코드
        'txtTrnClsfCd1': train.train_type,  # 열차 종류 (Train Class Code인듯)
        'txtSeatAttCd4': '15',  # ??? - 요구속성 (다른 번호는 창측/내측 이런거던데...)
        'txtPsgTpCd1': '1',  # ??? - 단체예약, 개인예약 구분이라는데...
        'txtJobId': '1101',  # 1101: 개인예약, 1102: 예약대기, 1103: SEATMAP예약
        'txtJrnyCnt': '1',  # 환승 횟수 (1이면 편도)
        'txtPsrmClCd1': '1',  # 1: 일반실, 2: 특실
        'txtJrnySqno1': '001',  # ???
        'txtJrnyTpCd1': '11',  # 편도
    }
    r = session.post(url, data=data)
    if 'w_mem01100.jsp' in r.text:
        print 'Need login!!'
        return False

    elif u'홈페이지주소를 잘못 입력하셨습니다.' in r.text:
        print u'Referer 오류'
        return False

    elif u'20분 이내 열차는' in r.text:
        print '20분 이내 열차는 예약하실 수 없습니다. 역창구 및 자동발매기를 이용하시기 바랍니다.'
        return False

    elif u'오류' in r.text:
        html = BeautifulSoup(r.text)
        error = html.select('.point02')
        print error[0].string.strip()
        return False

    elif 'w_adv03100.gif' in r.text:
        print 'Reservation Success!!'
        return True

    print 'Unhandled Error.'
    print r.text
    return False


def ticket_ids():
    """
    승차권 id 목록 조회
    """
    url = 'http://www.korail.com/pr/pr13500/w_pr13510.jsp'
    r = session.get(url)
    tickets = []
    pnrs = r.text.split("new pnr_info( '")
    for pnr in pnrs[1:]:
        ticket_id = pnr.split("'")[0]
        tickets.append(ticket_id)
    return tickets


def cancel(pnr_id):
    """
    예약취소

    :param pnr_id: 예약취소할 승차권 id
    """
    url = 'http://www.korail.com/servlets/pr.pr14500.sw_pr14514_i1Svt?'
    data = {
        'txtPnrNo': pnr_id,
        'txtLngScnt': '01',
        'txtJrnySqno': '001',
    }
    r = session.get(url, params=data)
    return u'정상적으로 취소가 완료되었습니다.' in r.text


phone = ''
password = ''
stations = all_stations()
dep_code = [station for station in stations if station[1] == u'서울'][0][0]
arr_code = [station for station in stations if station[1] == u'동대구'][0][0]
dep_date = datetime.strftime(datetime.now(), '%Y%m%d')
dep_time = datetime.strftime(datetime.now(), '%H%M%S')

print '서울역:', dep_code
print '동대구역:', arr_code

print 'Logging in...'
r = login(phone, password, True)
if not r:
    print 'Login failed.'
    exit()
print 'Login succeeded.'

trains = search(dep_code, arr_code, dep_date, dep_time, 2)
for t in trains:
    print t

reserve(trains[-1])

tickets = ticket_ids()
for ticket_id in tickets:
    if cancel(ticket_id):
        print 'Canceled reservation.'
