# coding:utf-8
"""
Create by Wangmeng Song
July 21,2017
"""

import shapefile as sf
from shapely.geometry import Polygon, Point
import os
import inspect
import numpy as np
import json

filedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "/" + "area"
filename = u'wholeArea.dbf'
eastarea = u'eastSide.dbf'
westoutside = u'westOutSide.dbf'
eastpick = u'eastPickUpArea.dbf'
westpick = u'westPickUpArea.dbf'
allpick = u'allPickUpArea.dbf'

class SIDE:
    def chengduArea(self, getonthecar, getonthecarLoc, getonthecarseatnum, RMMTSixpassengerOrderID, RMMTSixpassengerLoc, RMMTSixpassengerseatnum, northOrderID, northOrderLoc, northOrderSeatnum):
        latfilename = filedir + "/" + filename
        polys = sf.Reader(latfilename)
        polygon = polys.shapes()
        shpfilePoints = []
        for shape in polygon:
            shpfilePoints = shape.points
        polygon = Polygon(shpfilePoints)
        for i in range(len(RMMTSixpassengerLoc)):
            lng = RMMTSixpassengerLoc[i][1]
            lat = RMMTSixpassengerLoc[i][0]
            point = Point(lng, lat)
            if polygon.contains(point):
                northOrderID.append(RMMTSixpassengerOrderID[i])
                northOrderLoc.append(RMMTSixpassengerLoc[i])
                northOrderSeatnum.append(RMMTSixpassengerseatnum[i])
            else:
                getonthecar.append(RMMTSixpassengerOrderID[i])
                getonthecarLoc.append(RMMTSixpassengerLoc[i])
                getonthecarseatnum.append(RMMTSixpassengerseatnum[i])

    def ateast(self, northOrderLoc, orderNum):
        sideNo = np.zeros([orderNum], dtype=int)
        eastfilename = filedir + "/" + eastarea
        polys = sf.Reader(eastfilename)
        polygon = polys.shapes()
        shpfilePoints = []
        for shape in polygon:
            shpfilePoints = shape.points
        polygon = Polygon(shpfilePoints)
        for i in range(len(northOrderLoc)):
            lng = northOrderLoc[i][1]
            lat = northOrderLoc[i][0]
            point = Point(lng, lat)
            if polygon.contains(point):
                sideNo[i] = 1
            else:
                sideNo[i] = 2
        return sideNo

    def atwest2out(self, westLoc, orderNo):
        westsideNo = np.zeros([orderNo], dtype=int)
        westoutfilename = filedir + "/" + westoutside
        polys = sf.Reader(westoutfilename)
        polygon = polys.shapes()
        shpfilePoints = []
        for shape in polygon:
            shpfilePoints = shape.points
        polygon = Polygon(shpfilePoints)
        for i in range(len(westLoc)):
            lng = westLoc[i][1]
            lat = westLoc[i][0]
            point = Point(lng, lat)
            if polygon.contains(point):
                westsideNo[i] = 1         # 1表示在2环到2.5环之间
            else:
                westsideNo[i] = 2           # 2表示在西边2环内
        return westsideNo

    def orderinchengdutwofive(self, orderdata):
        latfilename = filedir + "/" + filename
        polys = sf.Reader(latfilename)
        polygon = polys.shapes()
        shpfilePoints = []
        for shape in polygon:
            shpfilePoints = shape.points
        polygon = Polygon(shpfilePoints)
        lng = orderdata['bdlng']
        lat = orderdata['bdlat']
        point = Point(lng, lat)
        if polygon.contains(point):
            orderdata['inside'] = 1
        else:
            orderdata['inside'] = 0
        jsondatar = json.dumps(orderdata, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        return jsondatar

    def eastpick(self, pickpoint):
        eastfile = filedir + "/" + eastpick
        polys = sf.Reader(eastfile)
        polygon = polys.shapes()
        shpfilePoints = []
        for shape in polygon:
            shpfilePoints = shape.points
        polygon = Polygon(shpfilePoints)
        lng = pickpoint[1]
        lat = pickpoint[0]
        point = Point(lng, lat)
        if polygon.contains(point):
            return True
        else:
            return False

    def westpick(self, pickpoint):
        westfile = filedir + "/" + westpick
        polys = sf.Reader(westfile)
        polygon = polys.shapes()
        shpfilePoints = []
        for shape in polygon:
            shpfilePoints = shape.points
        polygon = Polygon(shpfilePoints)
        lng = pickpoint[1]
        lat = pickpoint[0]
        point = Point(lng, lat)
        if polygon.contains(point):
            return True
        else:
            return False

    def allpick(self, pickpoint):
        allpickfile = filedir + "/" + allpick
        polys = sf.Reader(allpickfile)
        polygon = polys.shapes()
        shpfilePoints = []
        for shape in polygon:
            shpfilePoints = shape.points
        polygon = Polygon(shpfilePoints)
        lng = pickpoint[1]
        lat = pickpoint[0]
        point = Point(lng, lat)
        if polygon.contains(point):
            return True
        else:
            return False















