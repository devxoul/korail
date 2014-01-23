======
Korail
======

An unofficial Korail API for Python.


Installation
------------

You can install Korail with ``pip`` command like below:

::

    $ pip install korail



Quick Start
-----------

1. Login
~~~~~~~~

You can login to korail server via *membership number signing* or *phone number signing*.

Basically, to login via *membership number signing*:

::

    from korail import Korail
    
    korail = Korail()
    korail.login('12345678', '0000')  # membership number signing

Or via *phone number signing*:

::

    korail.login('010-1234-5678', '0000', True)  # phone number siging



2. Search Station
~~~~~~~~~~~~~~~~~

Search a station code with station name. All station code and name data is stored in ``stations.py`` file in package.

A single station data looks like:

::

    {
        "code": "0001",
        "name": u"서울"
    }

::

    stations = korail.search_station('서울')
    print stations[0]['code']  # '0001'



3. Search Train
~~~~~~~~~~~~~~~

You can search train schedules with ``search_train()`` method. ``search_train()`` method takes these arguments:

dep
    A departure station code.

arr
    An arrival station code.

date
    Departure date. (``yyyyMMdd`` formatted)

time (Default='000000')
    Departure time. (``hhmmss`` formatted)

train (Default='05')
    A train type. One of these:

    - 00: KTX
    - 01: 새마을호
    - 02: 무궁화호
    - 03: 통근열차
    - 04: 누리로
    - 05: 전체 (기본값)
    - 06: 공학직통
    - 09: ITX-청춘

count (Default=1)
    A number of passengers. Minimum value is 1 and maximum is 9.

Sample search code:

::

    dep = '0001'  # From: Seoul Station
    arr = '0015'  # To: Dong-Daegu Station
    date = '20140114'  # yyyyMMdd
    time = '001230'  # hhmmss

    # list of ``Trains`` instances.
    trains = korail.search_train(dep, arr, date, time)



4. Reservation
~~~~~~~~~~~~~~

::

    try:
        korail.reserve(train)
    except KorailError as e:
        print e.message



5. Get Tickets
~~~~~~~~~~~~~~

Retrieving all ticket information is not support yet. Only ticket id is returned.

::

    korail.tickets()



6. Cancel Ticket
~~~~~~~~~~~~~~~~

Example code below cancels all reserved tickets.

::

    for ticket_id in korail.tickets():
        korail.cancel_ticket(ticket_id)



To-Do
-----

1. Non-member reservation
2. More detailed exception handling
3. ``tickets()`` to return all ticket information.
