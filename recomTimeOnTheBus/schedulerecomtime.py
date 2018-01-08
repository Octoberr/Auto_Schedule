# coding:utf-8
"""
create Wangmeng Song
July 4,2017
增加功能
July 12,2017
"""
import shapefile as sf
from shapely.geometry import Polygon, Point, LinearRing
import datetime
import inspect
import os
from recomTimeOnTheBus import recommendtime

filedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "/" + "area"
filename = ['region1.dbf', 'region2.dbf', 'region3.dbf', 'region4.dbf', 'region5.dbf', 'region6.dbf']
PICKTIME = 3
DIFDURATION = 5
SAMEDURATION = 4
TIANFUSQUIRE = [30.604043, 104.074086]
BMAPAIRPORTCOORDINATE = [30.574590, 103.955020]


class TIMEANDAREA:
    def __init__(self, pickuptime, area):
        self.pickuptime = pickuptime
        self.area = area


class SCHEDULETIME:
    def getScheduleInfo(self, allSchedule, allOrderInfo):
        # allSchedule = [[[a,b,c],[e,d,f]],[[e,q,r],[t,y,u]]] 航段，车，订单
        # allOrderInfo = [{},{},{},{}]传入订单的详细信息
        detailSchedule = []  # [[{},{}],[{},{}]] 车，订单的详细信息
        for timetable in allSchedule:
            for car in timetable:
                newcar = []
                for orderNo in car:
                    res = [orderInfo['BID'] for orderInfo in allOrderInfo].index(orderNo)
                    newcar.append(allOrderInfo[res])
                    # for orderInfo in allOrderInfo:
                    #     if orderNo is orderInfo['BID']:
                detailSchedule.append(newcar)
        return detailSchedule

    def getpickuptime(self, resdict):
        # pktimeandarea = []
        point = Point(resdict['bdlng'], resdict['bdlat'])
        getdatetime = resdict['date']+resdict['startTime']
        # print type(getdatetime), getdatetime
        dateTime = datetime.datetime.strptime(getdatetime, "%Y-%m-%d%H:%M")
        # print type(datetime), dateTime
        # filename = self.getTxtNmae()
        # print "filename", filename
        for i in range(len(filename)):
            tmpfilename = filedir + "/" + filename[i]
            # print "tmpfilename:", tmpfilename
            polys = sf.Reader(tmpfilename)
            polygon = polys.shapes()
            shpfilePoints = []
            for shape in polygon:
                shpfilePoints = shape.points
            polygon = Polygon(shpfilePoints)
            if polygon.contains(point):
                getonthncartime = dateTime + datetime.timedelta(minutes=i*10)
                TIMEANDAREA.pickuptime = getonthncartime
                TIMEANDAREA.area = i
                # print "上车时间:", getonthncartime
                # pktimeandarea.append(getonthncartime)
                # pktimeandarea.append(i)
                break
            else:
                continue
                # print "no data"
        return TIMEANDAREA

    def unixtimeToBjTime(self, nowUnixtime):
        bjtime = datetime.datetime.fromtimestamp(nowUnixtime)
        return bjtime

    def incressPickupTime(self, allSchedule, allOrderInfo):
        from sendtoairport import auxfn
        re = recommendtime.RECOMDTIME()
        allcar = self.getScheduleInfo(allSchedule, allOrderInfo)
        for car in allcar:
            if len(car) == 1:  # 整辆车只有一个订单的情况
                if 'pickupTime' not in car[0].keys() or car[0]['driver'] is None or car[0]['driver'] is u"":
                    timeandare = self.getpickuptime(car[0])
                    # unixpickuptime = int(time.mktime((timeandare.pickuptime).timetuple()))
                    car[0]['pickupTime'] = str(timeandare.pickuptime)
            else:   # 整辆车拥有很多订单
                orderdisVec = []
                for order in car:
                    orderdisVec.append((order['bdlat'], order['bdlng']))
                orderVec = re.getOrderLocVec(orderdisVec)
                disVec = auxfn.calcDistVec(TIANFUSQUIRE, orderVec)
                distSort = sorted(range(len(disVec)), key=lambda k: disVec[k], reverse=True)
                firstpktimeandarea = self.getpickuptime(car[distSort[0]])
                starttime = firstpktimeandarea.pickuptime
                currentarea = firstpktimeandarea.area
                # if 'pickupTime' not in car[0].keys() or car[0]['driver'] is None or car[0]['driver'] is u"":
                pickuptime = starttime
                # unixpickuptime = int(time.mktime(pickuptime.timetuple()))
                car[distSort[0]]['pickupTime'] = str(pickuptime)
                # else:
                #     pickuptime = self.unixtimeToBjTime(car[0]['pickupTime'])
                for i in range(1, len(distSort)):
                    nextpktimeandarea = self.getpickuptime(car[distSort[i]])
                    nextarea = nextpktimeandarea.area
                    # if 'pickupTime' not in car[i].keys() or car[i]['driver'] is None or car[i]['driver'] is u"":
                    areacount = abs(nextarea - currentarea)
                    if areacount == 0:
                        pickuptime += datetime.timedelta(minutes=PICKTIME) + datetime.timedelta(minutes=SAMEDURATION)
                    else:
                        pickuptime += datetime.timedelta(minutes=PICKTIME) + datetime.timedelta(minutes=DIFDURATION * areacount)
                    # unixpickuptime = int(time.mktime(pickuptime.timetuple()))
                    car[distSort[i]]['pickupTime'] = str(pickuptime)
                    # else:
                    #     pickuptime = self.unixtimeToBjTime(car[i]['pickupTime'])
                    currentarea = nextarea
        return allcar
    # def incresspickuptime(self, allSchedule, allOrderInfo):
    #     allcar = self.getScheduleInfo(allSchedule, allOrderInfo)
    #     for car in allcar:
    #         if len(car) is 1:
    #             pickuptimeandarea = self.getpickuptime(car[0])
    #             unixpickuptime = int(time.mktime(pickuptimeandarea[0].timetuple()))
    #             car[0]['pickupTime'] = unixpickuptime
    #         else:
    #             firstpktimeandarea = self.getpickuptime(car[0])
    #             starttime = firstpktimeandarea[0]
    #             currentarea = firstpktimeandarea[1]
    #             unixpickuptime = int(time.mktime(starttime.timetuple()))
    #             car[0]['pickupTime'] = unixpickuptime
    #             for i in range(1, len(car)):
    #                 nextpktimeandarea = self.getpickuptime(car[i])
    #                 nextarea = nextpktimeandarea[1]
    #                 areacount = abs(nextarea - currentarea)
    #                 if areacount is 0:
    #                     starttime += datetime.timedelta(minutes=PICKTIME) + datetime.timedelta(minutes=SAMEDURATION)
    #                 else:
    #                     starttime += datetime.timedelta(minutes=PICKTIME) + datetime.timedelta(minutes=DIFDURATION*areacount)
    #                 unixpickuptime = int(time.mktime(starttime.timetuple()))
    #                 car[i]['pickupTime'] = unixpickuptime
    #                 currentarea = nextarea
    #     return allcar




