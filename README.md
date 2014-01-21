# Korail API Documentation

### 열차 검색

#### URL

http://www.korail.com/servlets/pr.pr21100.sw_pr21111_i1Svt

#### Method

GET

#### Arguments


##### radJobId

여정/경로

* 1: 직통
* 2: 환승
* 3: 왕복
* Y: 일부구간동행


##### txtGoAbrdDt

출발일시 (yyyyMMdd)


##### txtGoStart

출발역

EUC-KR로 인코딩된 역이름의 escape된 문자열


##### txtGoEnd

도착역

EUC-KR로 인코딩된 역이름의 escape된 문자열


##### checkStnNm

`Y`로 설정될 경우 출발역, 도착역을 문자열로 검사한다. `N`일 경우 `txtGoStartCode`, `txtGoEndCode`가 추가로 제공되어야 한다.


##### selGoTrain

열차 종류

* 00: KTX
* 01: 새마을호
* 02: 무궁화호
* 03: 통근열차
* 04: 누리로
* 05: 전체
* 06: 공학직통
* 09: ITX-청춘