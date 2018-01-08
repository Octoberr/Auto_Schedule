# coding:utf-8
"""
create Wangmeng Song
July 4,2017
overwrite by Wangmeng Song 
July 17,2017
修改固定上车时间
July 20,2017
"""

import shapefile as sf
from shapely.geometry import Polygon, Point, LinearRing
import os
import datetime
import numpy as np
import inspect
import copy
import json
import requests

PICKTIME = 3
DIFDURATION = 5
SAMEDURATION = 4
BMAPAIRPORTCOORDINATE = [30.574590, 103.955020]  # 成都机场
TIANFUSQUIRE = [30.604043, 104.074086]

filedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "/" + "area"
filename = ['region1.dbf', 'region2.dbf', 'region3.dbf', 'region4.dbf', 'region5.dbf', 'region6.dbf']
# 测试环境
# TimeTableInfoURL = 'https://prerelease.jichangzhuanxian.com/api/ShiftTime/GetShiftTimeByTakeOffTime'
# 正式环境
TimeTableInfoURL = 'https://mgr.jichangzhuanxian.com/api/ShiftTime/GetShiftTimeByTakeOffTime'


class TIMEANDAREA:
    def __init__(self, pickuptime, area):
        self.pickuptime = pickuptime
        self.area = area


class RECOMDTIME:
    def getorderareanum(self, lng, lat):
        point = Point(lng, lat)
        # getdatetime = resdict['date']+resdict['startTime']
        # print type(getdatetime), getdatetime
        # dateTime = datetime.datetime.strptime(getdatetime, "%Y-%m-%d%H:%M")
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
                # getonthncartime = dateTime + datetime.timedelta(minutes=i*10)
                areanum = i
                # print "上车时间:", getonthncartime
                return areanum
            else:
                continue
                # print "no data"

    def getOrderLocVec(self, orderLocList):
        orderLocVec = np.zeros([len(orderLocList), 2], dtype=float)
        for i in range(len(orderLocList)):
            orderLocVec[i][0] = orderLocList[i][0]
            orderLocVec[i][1] = orderLocList[i][1]
        return orderLocVec

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

    def getonthecardata(self, resdict):
        from sendtoairport import auxfn
        neworderinfo = copy.copy(resdict)
        orderdisVec = []
        for order in neworderinfo:
            orderdisVec.append((order['bdlat'], order['bdlng']))
        orderVec = self.getOrderLocVec(orderdisVec)
        disVec = auxfn.calcDistVec(TIANFUSQUIRE, orderVec)
        distSort = sorted(range(len(disVec)), key=lambda k: disVec[k], reverse=True)
        if len(distSort) == 1:  # 整辆车只有一个订单的情况
            if 'pickupTime' not in neworderinfo[distSort[0]].keys() or neworderinfo[distSort[0]]['pickupTime'] is None or neworderinfo[distSort[0]]['pickupTime'] is u"":
                timeandare = self.getpickuptime(neworderinfo[0])
                # unixpickuptime = int(time.mktime((timeandare.pickuptime).timetuple()))
                neworderinfo[0]['pickupTime'] = str(timeandare.pickuptime)
            else:
                strpickuptime = neworderinfo[distSort[0]]['pickupTime']
                pickuptime = datetime.datetime.strptime(strpickuptime, "%Y-%m-%dT%H:%M:%S")
                neworderinfo[0]['pickupTime'] = str(pickuptime)
        else:  # 整辆车拥有很多订单
            firstpktimeandarea = self.getpickuptime(neworderinfo[distSort[0]])
            currentarea = firstpktimeandarea.area
            if 'pickupTime' not in neworderinfo[distSort[0]].keys() or neworderinfo[distSort[0]]['pickupTime'] is None or neworderinfo[distSort[0]]['pickupTime'] is u"":
                starttime = firstpktimeandarea.pickuptime
                pickuptime = starttime
                neworderinfo[distSort[0]]['pickupTime'] = str(pickuptime)
            else:
                strpickuptime = neworderinfo[distSort[0]]['pickupTime']
                pickuptime = datetime.datetime.strptime(strpickuptime, "%Y-%m-%dT%H:%M:%S")
                neworderinfo[distSort[0]]['pickupTime'] = str(pickuptime)
            for i in range(1, len(distSort)):
                nextpktimeandarea = self.getpickuptime(neworderinfo[distSort[i]])
                nextarea = nextpktimeandarea.area
                if 'pickupTime' not in neworderinfo[distSort[i]].keys() or neworderinfo[distSort[i]]['pickupTime'] is None or neworderinfo[distSort[i]]['pickupTime'] is u"":
                    areacount = abs(nextarea - currentarea)
                    if areacount == 0:
                        pickuptime += datetime.timedelta(minutes=PICKTIME) + datetime.timedelta(minutes=SAMEDURATION)
                    else:
                        pickuptime += datetime.timedelta(minutes=PICKTIME) + datetime.timedelta(minutes=DIFDURATION * areacount)
                    neworderinfo[distSort[i]]['pickupTime'] = str(pickuptime)
                else:
                    strpickuptime = neworderinfo[distSort[i]]['pickupTime']
                    pickuptime = datetime.datetime.strptime(strpickuptime, "%Y-%m-%dT%H:%M:%S")
                    neworderinfo[distSort[i]]['pickupTime'] = str(pickuptime)
                currentarea = nextarea
        jsondatar = json.dumps(neworderinfo, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        return jsondatar

    def firstGetTime(self, order):
        info = copy.copy(order)
        orderlng = info['bdlng']
        orderlat = info['bdlat']
        # get the area number
        areanum = self.getorderareanum(orderlng, orderlat)
        # 1、获得飞机起飞时间
        planetakeofftime = info['takeofftime']
        # 2、获得航段
        res = requests.post(TimeTableInfoURL, json={"Time": planetakeofftime})
        dataInfo = res.json()["Data"][0]
        timetable = dataInfo['TimeCode']
        # 3、获得航段的接送开始时间
        starttime = dataInfo['PickupStartTime']
        getdatetime = info['date'] + starttime
        dateTime = datetime.datetime.strptime(getdatetime, "%Y-%m-%d%H:%M")
        getOnTheCarTime = dateTime + datetime.timedelta(minutes=areanum*10)
        # info['pickupTime'] = int(time.mktime(getOnTheCarTime.timetuple()))
        info['TimeTable'] = timetable
        info['pickupTime'] = str(getOnTheCarTime)
        # print "转换信息",info
        jsondatar = json.dumps(info, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        # print "jsondata", jsondatar
        return jsondatar
        # return txtname

    def gettheordertime(self):
        polys = sf.Reader("shapefiles/test/wholeArea.shp")
        polygon = polys.shapes()
        shpfilePoints = []
        for shape in polygon:
            shpfilePoints = shape.points
        polygon = Polygon(shpfilePoints)

        # #[锦里，九眼桥，锦江宾馆, 仁恒置地, 桐梓林, 骡马寺]
        # currentPoint = [30.662447, 104.072469] # 天府广场
        # points = [[30.650817,104.056385], [30.645582,104.095192], [30.654087,104.072528],
        #             [30.658646,104.072563], [30.621274,104.073749], [30.672531,104.071962]]
        # destination = [30.599595,104.040745] # 交界点

        point = Point(104.072469, 30.662447)  # 天府广场
        # point = Point(104.040745,30.599595) # keyPoint
        # point = Point(104.042779,30.620844)
        # point in polygon test
        if polygon.contains(point):
            print 'inside'
        else:
            print 'OUT'
            polExt = LinearRing(polygon.exterior.coords)
            d = polExt.project(point)
            p = polExt.interpolate(d)
            closest_point_coords = list(p.coords)[0]
            print list(p.coords)
            print d
