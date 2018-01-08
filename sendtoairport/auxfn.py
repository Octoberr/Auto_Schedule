# coding:utf-8

"""
Donghui Chen, Wangmeng Song
May 15, 2017
修改 Wangmeng Song
June 21, 2017
July 21,2017
"""

import math
import geopy.distance
import numpy as np
from scipy import inf
from sklearn.neighbors import NearestNeighbors

# 分割线左边判断角度的点和距离
leftCheckDirection = [30.610773, 104.040650]
# 分割线右边判断角度的点
rightCheckDirection = [30.604043, 104.074086]
TIANFUSQUIRE = [30.604043, 104.074086]

AMAPKEYCOORDINATE = [30.599374, 104.040454]  # 高速交汇点


class Location:
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng


def getListArrayDim(self, ainput, dim=0):

    """
    get the dimension of a list
    returns -1 if it is no list at all, 0 if list is empty 
    and otherwise the dimensions of it
    """
    if isinstance(ainput, (list, np.ndarray)):
        if ainput == []:
            return dim
        dim = dim + 1
        dim = self.getListArrayDim(ainput[0], dim)
        return dim
    else:
        if dim == 0:
            return -1
        else:
            return dim


# 百度坐标转高德坐标
def BD2AMap(bdLat, bdLng):
    """
    Coordinate convertion: from BD to Gaode 
    """
    #因为没有使用高德计算时间的接口所以改回百度
    # x_pi = 3.14159265358979324 * 3000.0 / 180.0
    # x = bdLng - 0.0065
    # y = bdLat - 0.006
    # z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    # theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    # AMapLng = z * math.cos(theta)
    # AMapLat = z * math.sin(theta)
    return Location(bdLat, bdLng)


def calcDist(locationA, locationB):
    """ 
    input: two location coordinates: (latA, lngA) & (latB, lngB), could be tuple or list
    output: the distance of two location measuring in meters.
    """
    return geopy.distance.vincenty(locationA, locationB).km * 1000


def calcDistVec(destination, originVec):
    """
    destination: a list saving [lat, lng]
    originVec: a 2-dimensional array
    """
    if isinstance(originVec, (tuple, list)): 
        if getListArrayDim(originVec) == 1: 
            numLocation = 1
        else:
            numLocation = len(originVec)
    elif isinstance(originVec, np.ndarray): 
        numLocation = originVec.shape[0]
    else:
        print "wrong input type in calcDistVec, originVec."
        return
    distVec = np.zeros([numLocation], dtype=int)
    for i in xrange(numLocation):
        distVec[i] = calcDist(destination, originVec[i])
    return distVec


# def getNeighborhoodIdx(points, center, radius):
#     # the distance of two points is defined as sqrt( (latA-latB)^2 + (lngA-lngB)^2 )
#     # distance of 0.01 in lats and lngs is about 1.1km
#     if len(points) == 1:
#         neighborhoodIdx = [0]
#         return neighborhoodIdx
#     tree = cKDTree(points)
#     neighborhoodIdx = []                   # Put the neighbors of each point here
#     distances, indices = tree.query(center, len(points), p=2, distance_upper_bound=radius)
#     for index, distance in zip(indices, distances):
#         if distance == inf:
#             break
#         neighborhoodIdx.append(index)
#     return neighborhoodIdx
# 寻找周围的的人东为1，西为2，1的两边可以选，2就只能选2
def getNeighborhoodIdx(points, center, radius, firstPassengerIdx, sidevec):
    # the distance of two points is defined as sqrt( (latA-latB)^2 + (lngA-lngB)^2 )
    # distance of 0.01 in lats and lngs is about 1.1km
    listCenter = [center]
    listPoints = points.tolist()
    if len(points) == 1:
        neighborhoodIdx = [0]
        return neighborhoodIdx
    neighborhoodIdx = []                   # Put the neighbors of each point here
    neigh = NearestNeighbors(n_neighbors=len(listPoints), metric=calcDist)
    neigh.fit(points)
    distances, indices = neigh.kneighbors(listCenter)
    for index, distance in zip(indices, distances):
        npIndex = index
        npDistance = distance
    if sidevec[firstPassengerIdx] == 1:   # 1可以选择1或者2
        for i in range(len(npIndex)):
                if npDistance[i] <= radius:
                    neighborhoodIdx.append(npIndex[i])
                else:
                    break
    else:
        for i in range(len(npIndex)):
            if sidevec[npIndex[i]] == 2:   # 2就只能选择2
                if npDistance[i] <= radius:
                    neighborhoodIdx.append(npIndex[i])
                else:
                    break
    return neighborhoodIdx


def checkDistCondition(currentPoint, nextPoint, destination):
    # 检查下一个地点是否比现在的位置更靠近终点
    currentDist = calcDist(currentPoint, destination)
    nextDist = calcDist(nextPoint, destination)
    if currentDist >= nextDist:
        return True
    else:
        return False


def angleBetweenVectorsDegrees(A, vertex, C):
    """Return the angle between two vectors in any dimension space,
    in degrees."""
    # Convert the points to numpy latitude/longitude radians space
    a = np.radians(np.array(A))
    vertexR = np.radians(np.array(vertex))
    c = np.radians(np.array(C))
    # Vectors in latitude/longitude space
    sideA = a - vertexR
    sideC = c - vertexR
    # Adjust vectors for changed longitude scale at given latitude into 2D space
    lat = vertexR[0]
    sideA[1] *= math.cos(lat)
    sideC[1] *= math.cos(lat)
    direct = np.degrees(math.acos(np.dot(sideA, sideC) / (np.linalg.norm(sideA) * np.linalg.norm(sideC))))
    return direct


def checkDirectionCondition(currentPoint, nextPoint):
    # 检查下一个地点是否与现在的行驶方向顺路，顺路的定义是夹角小于maxAngle
    # 角度随到天府交汇点的距离递增
    nextPointToTianFudist = calcDist(nextPoint, TIANFUSQUIRE)
    if nextPointToTianFudist > 8000:
        MAXANGLE = 16
    elif nextPointToTianFudist > 5000 and nextPointToTianFudist <= 8000:
        MAXANGLE = 21
    elif nextPointToTianFudist > 3500 and nextPointToTianFudist <= 5000:
        MAXANGLE = 26
    elif nextPointToTianFudist <= 3500:
        MAXANGLE = 36
    if angleBetweenVectorsDegrees(currentPoint, rightCheckDirection, nextPoint) <= MAXANGLE:
        return True
    elif angleBetweenVectorsDegrees(currentPoint, leftCheckDirection, nextPoint) <= MAXANGLE:
        return True
    else:
        return False


# 当前点side为1可以选择所有的点找周围的点，当前点为2就只能找2
def getSortedPointIdx(points, currentPoint, sidevec, currenside):
    from recomTimeOnTheBus import eastandwestside
    # 获取当前点到所有订单地点的距离按照从小到大排序
    # 获取当前点到其余所有点的距离
    sd = eastandwestside.SIDE()
    listCurrentPoint = list(currentPoint)
    pointDistVec = calcDistVec(listCurrentPoint, points)
    # 获得pointDistVec从小到大的index排序[2,0,1,3]!!!下标排序
    pointSotedIndex = sorted(range(len(pointDistVec)), key=lambda k: pointDistVec[k])
    closestPointIdx = []
    if currenside == 1:
        for index in pointSotedIndex:
            if checkDistCondition(currentPoint, points[index], AMAPKEYCOORDINATE) and \
                    checkDirectionCondition(currentPoint, points[index]):
                closestPointIdx.append(index)
                continue
            elif sd.eastpick(points[index]):
                closestPointIdx.append(index)
                continue
            elif sd.westpick(points[index]):
                closestPointIdx.append(index)
                continue
            else:
                continue
        return closestPointIdx
    else:
        for index in pointSotedIndex:
            if sidevec[index] == 2:
                if checkDistCondition(currentPoint, points[index], rightCheckDirection) and \
                        checkDirectionCondition(currentPoint, points[index]):
                    closestPointIdx.append(index)
                    continue
                elif sd.westpick(points[index]):
                    closestPointIdx.append(index)
                    continue
                else:
                    continue
            else:
                continue
        return closestPointIdx


def getAllIndices(element, alist):
    """
    Find the index of an element in a list. The element can appear multiple times.
    input:  alist - a list
            element - objective element
    output: index of the element in the list
    """
    result = []
    offset = -1
    while True:
        try:
            offset = alist.index(element, offset + 1)
        except ValueError:
            return result
        result.append(offset)