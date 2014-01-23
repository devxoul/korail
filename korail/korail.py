# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests


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


class Korail(object):

    #: A `requests` session.
    session = requests.session()

    #: Static stations data from `stations.json`.
    stations = None

    def all_stations(self):
        """Load all stations from Korail server. Recommend using static json
        file instead.
        """
        stations = []
        for i in range(14):
            url = 'http://www.korail.com/servlets/pr.pr11100.sw_pr11111_f1Svt'
            params = {
                'hidKorInx': i,  # an index for '가'~'하'
            }
            r = requests.get(url, params=params)
            html = r.text.split('<table class="s-view">')[3]
            rows = html.split("javascript:putStation('")[1:]
            for row in rows:
                name = row.split("'")[0]
                code = row.split(",'")[1].split("'")[0]
                stations.append(dict(code=code, name=name))
        return stations

    def search_station(self, query):
        """Search stations with name from `self.stations`.

        :param query: A searching query.
        """
        import stations
        return [s for s in stations.stations if query in s['name']]

    def login(self, id, password, use_phone=False):
        """Login to Korail server.

        :param id: Korail membership number or phone number. Phone number
                   should be authenticated for using phone number signing.
        :param password: A password.
        :param use_phone: `True` for use phone number signing.
        """
        url = 'https://www.korail.com/servlets/hc.hc14100.sw_hc14111_i2Svt'
        data = {
            # '2' for membership number signing
            # '4' for phone number signing
            'selInputFlg': '4' if use_phone else '2',
            'UserId': id,
            'UserPwd': password,
            'hidMemberFlg': '1',  # 없으면 입력값 오류
        }
        r = self.session.post(url, data=data)

        # if succeeded, html page shows redirect javascript code.
        if 'w_mem01106' in r.text:
            return True
        return False

    def logout(self):
        url = 'http://www.korail.com/2007/mem/mem01000/w_mem01102.jsp'
        self.session.get(url)

    def search_train(self, dep, arr, date, time='000000', train='05', count=1):
        """Search trains.

        :param dep: A departure station code.
        :param arr: An arrival station code.
        :param date: A departure date. `yyyyMMdd` formatted.
        :param time: A departure time. `hhmmss` formatted.
        :param train: A type of train.
                      - 00: KTX
                      - 01: 새마을호
                      - 02: 무궁화호
                      - 03: 통근열차
                      - 04: 누리로
                      - 05: 전체 (기본값)
                      - 06: 공학직통
                      - 09: ITX-청춘
        :param count: Passengers count. Minimum is 1, maximum is 9.
        """
        url = 'http://www.korail.com/servlets/pr.pr21100.sw_pr21111_i1Svt'
        params = {
            'txtGoAbrdDt': date,
            'txtGoHour': time,
            'txtGoStartCode': dep,
            'txtGoEndCode': arr,
            'checkStnNm': 'N',
            'radJobId': '1',  # 직통
            'txtPsgCnt1': count,
        }
        r = self.session.get(url, params=params)

        html = BeautifulSoup(r.text)

        # A div class 'point02' represents an error message.
        error = html.select('.point02')
        if error:
            raise KorailError(error[0].string.strip())

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

            # 특실
            img = td7s[0].select('img')
            content = img[0] if img else td7s[0].contents[0]
            train.first_class = 'yes' in content.__str__()

            # 일반실
            img = td7s[1].select('img')
            content = img[0] if img else td7s[0].contents[0]
            train.general_admission = 'yes' in content.__str__()

            trains.append(train)
            i += 1

        return trains

    def reserve(self, train):
        """Reserve a train.

        :param train: An instance of `Train`.
        """

        # reservation server checks referer.
        self.session.headers = {
            'Referer':
            'http://www.korail.com/servlets/pr.pr21100.sw_pr21111_i1Svt'
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
        r = self.session.post(url, data=data)

        # if not logged in, server returns redirect script.
        if 'w_mem01100.jsp' in r.text:
            raise KorailError("로그인이 필요합니다.")

        elif u"홈페이지주소를 잘못 입력하셨습니다." in r.text:
            raise KorailError("홈페이지주소를 잘못 입력하셨습니다. Referer를 확인해주세요.")

        elif u"20분 이내 열차는" in r.text:
            raise KorailError("20분 이내 열차는 예약하실 수 없습니다. "
                              "역창구 및 자동발매기를 이용하시기 바랍니다.")

        elif u'오류' in r.text:
            html = BeautifulSoup(r.text)
            error = html.select('.point02')
            raise KorailError(error[0].string.strip())

        elif 'w_adv03100.gif' in r.text:
            return True

        raise KorailError("Unhandled Error")

    def tickets(self):
        """Get my ticket ids.
        """
        tickets = []
        page = 1
        while True:
            url = 'http://www.korail.com/pr/pr13500/w_pr13510.jsp'
            params = dict(hidSelPage=page)
            r = self.session.get(url, params=params)
            pnrs = r.text.split("new pnr_info( '")
            if len(pnrs) < 2:
                break
            for pnr in pnrs[1:]:
                ticket_id = pnr.split("'")[0]
                tickets.append(ticket_id)
            page += 1
        return tickets

    def cancel_ticket(self, ticket_id):
        """Cancel reservation.

        :param pnr_id: A ticket id for cancelatino.
        """
        url = 'http://www.korail.com/servlets/pr.pr14500.sw_pr14514_i1Svt?'
        data = {
            'txtPnrNo': ticket_id,
            'txtLngScnt': '01',
            'txtJrnySqno': '001',
        }
        r = self.session.get(url, params=data)
        return u"정상적으로 취소가 완료되었습니다." in r.text


class KorailError(Exception):

    def __init__(self, message):
        self.message = message
