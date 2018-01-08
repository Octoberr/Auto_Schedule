# coding:utf-8

"""
create by swm
september, 13, 2017
"""
import os
import inspect
import shapefile as sf
from shapely.geometry import Polygon, Point, LinearRing
import geopy.distance
neighborlist = ['area1.dbf', 'area2.dbf', 'area3.dbf', 'area4.dbf', 'area5.dbf', 'area6.dbf', 'area7.dbf', 'area8.dbf',
                'area9.dbf', 'area10.dbf', 'area11.dbf', 'area12.dbf', 'area13.dbf', 'area14.dbf', 'area15.dbf',
                'area16.dbf', 'area17.dbf', 'area18.dbf', 'area19.dbf', 'area20.dbf', 'area21.dbf', 'area22.dbf',
                'area23.dbf', 'area24.dbf', 'area25.dbf', 'area26.dbf', 'area27.dbf', 'area28.dbf']
filedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "/" + "neighbor"


def findtheareanumber(loclat, loclng):
    point = Point(loclng, loclat)
    for i in range(len(neighborlist)):
        areanum = 0
        tmpfilename = filedir + "/" + neighborlist[i]
        polys = sf.Reader(tmpfilename)
        polygon = polys.shapes()
        shpfilePoints = []
        for shape in polygon:
            shpfilePoints = shape.points
        polygon = Polygon(shpfilePoints)
        if polygon.contains(point):
            areanum = i
            return areanum
        elif i == len(neighborlist) - 1 and areanum == 0:
            return None


def calcDist(locationA, locationB):
    """
    input: two location coordinates: (latA, lngA) & (latB, lngB), could be tuple or list
    output: the distance of two location measuring in meters.
    """
    return geopy.distance.vincenty(locationA, locationB).km * 1000


def theneighborarea(arealoclist, allgetonthecaridx, currentarea, restorderLoc, currentpointneighbor):
    allneighboridx = []
    for areaidx in currentpointneighbor:
        index = [i for i in range(len(arealoclist)) if arealoclist[i] == areaidx and i not in allgetonthecaridx]
        allneighboridx += index
    if len(allneighboridx) == 0:
        return None
    else:
        less100idx = []
        less100element = []
        # 当前点所在的区域
        filename = filedir + "/" + neighborlist[currentarea]
        polys = sf.Reader(filename)
        polygon = polys.shapes()
        shpfilePoints = []
        for shape in polygon:
            shpfilePoints = shape.points
        polygon = Polygon(shpfilePoints)   # or Polygon(shpfilePoints)
        for neighbor in allneighboridx:
            point = Point(restorderLoc[neighbor][1], restorderLoc[neighbor][0])
            polExt = LinearRing(polygon.exterior.coords)
            d = polExt.project(point)
            p = polExt.interpolate(d)
            closest_point_coords = list(p.coords)[0]
            # print calcDist((104.042779, 30.620844), (closest_point_coords[0], closest_point_coords[1]))
            distance = calcDist((restorderLoc[neighbor][1], restorderLoc[neighbor][0]), (closest_point_coords[0], closest_point_coords[1]))
            if distance < 101:
                less100idx.append(neighbor)
                less100element.append(distance)
        if len(less100idx) > 1:
            newsortneighbor = [idx for (element, idx) in sorted(zip(less100element, less100idx))]
            return newsortneighbor
        elif len(less100idx) == 1:
            return less100idx
        else:
            return None


def getthewestneighbor(area26, westarealoclist, westorderLoc):
    allneighboridx = []
    for areaidx in area26:
        index = [i for i in range(len(westarealoclist)) if westarealoclist[i] == areaidx]
        allneighboridx += index
    if len(allneighboridx) == 0:
        return []
    else:
        less100idx = []
        less100element = []
        # 当前点所在的区域
        filename = filedir + "/" + neighborlist[25]
        polys = sf.Reader(filename)
        polygon = polys.shapes()
        shpfilePoints = []
        for shape in polygon:
            shpfilePoints = shape.points
        polygon = Polygon(shpfilePoints)   # or Polygon(shpfilePoints)
        for neighbor in allneighboridx:
            point = Point(westorderLoc[neighbor][1], westorderLoc[neighbor][0])
            polExt = LinearRing(polygon.exterior.coords)
            d = polExt.project(point)
            p = polExt.interpolate(d)
            closest_point_coords = list(p.coords)[0]
            # print calcDist((104.042779, 30.620844), (closest_point_coords[0], closest_point_coords[1]))
            distance = calcDist((westorderLoc[neighbor][1], westorderLoc[neighbor][0]), (closest_point_coords[0], closest_point_coords[1]))
            if distance < 101:
                less100idx.append(neighbor)
                less100element.append(distance)
        if len(less100idx) > 1:
            newsortneighbor = [idx for (element, idx) in sorted(zip(less100element, less100idx))]
            return newsortneighbor
        else:
            return less100idx







