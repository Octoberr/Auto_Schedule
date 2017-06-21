# coding:utf-8

"""
Donghui Chen, Wangmeng Song
May 15, 2017
排班逻辑修改 Wangmeng Song
June 20, 2017
"""

import numpy as np
from compiler.ast import flatten
import threading
import copy

import schedule
import mapAPI
import auxfn

AMAPKEYCOORDINATE = [30.593084, 104.034047]  # 高速交汇点
AMAPAIRPORTCOORDINATE = [30.574590, 103.955020]  # 成都机场
TIANFUSQUIRE = [30.598071, 104.067665]
SEARCHRADIUS = 1500  # 1500m的范围
CARSEATS = 6     # 一辆车最大乘客为6个人
TIMELIMIT = 6000    # 时间限制为6000s
# event = threading.Event()  # 设置全局变量event为True


def startschedul(resdict):
    # ------------------
    # initialization
    # event.wait()    # 设置全局变量event为false,是其他线程处于等待状态
    dis = schedule.DIST()   # 实例化DIST类
    GTI = mapAPI.AMapAPI()   # 实例化AMapAPI类
    arrangedPassengerIdx = []  # store order index on all cars
    currentScheduleVec = []  # temporary using, store each passenger's travelling time on the same car
    time2AirportVec = []  # store each passenger's travelling time
    numPassengerVec = []  # store the number of passengers on each car
    # ------------------
    # Get all the order coordinates, save in a 2D-array, 1st row is latitude, 2nd row is longitude
    getonthecar = []  # [[A,,B,C],[D,E,F]] 存储一个地点==5or6的订单
    getonthecarLoc = []  # [(lat1,lng1),(lat2,lng2)] 存储一个地点==5or6的lat,lng
    getonthecarseatnum = []  # [[1,2,3],[2,3]] 存储一个地点==5or6的乘客人数
    repeatpoid = []     # 存储第一次处理的传入数据的订单号
    repeatloc = []      # 存储第一次处理的传入数据的经纬度
    repeatseatnum = []      # 存储第一次处理的传入数据的乘客人数
    # 处理第一次传入的数据，第一次处理：过滤一个订单乘客人数==5or6
    dis.getAllRepeatData(repeatpoid, repeatloc, repeatseatnum, getonthecar, getonthecarLoc, getonthecarseatnum, resdict)
    duplicateOrderID = []   # 存储第二次处理的传入数据的订单号
    duplicateSeatNum = []   # 存储第二次处理的传入数据的乘客人数
    # 获得第二次处理的传入数据的经纬度，第二次处理：获取一个地点的订单号，获取一个地点的乘客人数，获取唯一的经纬度
    duplicateLoc = dis.getDuplicateData(repeatpoid, repeatloc, repeatseatnum, duplicateOrderID, duplicateSeatNum)
    RMMTSixpassengerOrderID = []    # 存储第三次处理的传入数据的订单号
    RMMTSixpassengerLoc = []        # 存储第三次处理的传入数据的经纬度
    RMMTSixpassengerseatnum = []    # 存储第三次处理的传入数据的乘客人数
    # 第三次处理，过滤一个地点乘客人数==5or6
    dis.removeMoreThanSixPassenger(duplicateOrderID, duplicateLoc, duplicateSeatNum,
                                   RMMTSixpassengerOrderID, RMMTSixpassengerLoc, RMMTSixpassengerseatnum,
                                   getonthecar, getonthecarLoc, getonthecarseatnum)
    if len(getonthecarLoc) is not 0:
        # 寻找一个地点乘客人数==5的周围是否存在1个订单1个人的情况
        dis.getTheFivePersonAroundOnlyOne(getonthecar, getonthecarLoc, getonthecarseatnum,
                                          RMMTSixpassengerOrderID, RMMTSixpassengerLoc, RMMTSixpassengerseatnum)
    orderNum = len(RMMTSixpassengerLoc)     # 进入排班算法的总地点数
    if orderNum > 1:
        orderVec = dis.getOrderLocVec(RMMTSixpassengerLoc)     # 一维的经纬度列表转换为二维的经纬度数组
        seatNumVec = dis.getOrderNumVec(RMMTSixpassengerseatnum)    # 二维的乘客人数转换为与地点对应的一维数组
        keypointDistVec = auxfn.calcDistVec(TIANFUSQUIRE, orderVec)    # 获取每个地点到天府高速交汇点的一维数组
        # Calculate the time distance from airport for each order
        airportTimeDistVec = GTI.getTimeDistVec(AMAPAIRPORTCOORDINATE, orderVec, orderNum)  # 获取每个地点到机场的时间距离
        while len(arrangedPassengerIdx) < orderNum:
            firstPassengerIdx = np.argmax(keypointDistVec)  # 寻找距离机场最远的第一个上车的人
            arrangedPassengerIdx.append(firstPassengerIdx)  # 存储地点位置的索引[3,4,1,0]
            currentScheduleVec.append(airportTimeDistVec[firstPassengerIdx])  # 存储时间的索引，2017/6/19时间已经不再使用
            numPassenger = seatNumVec[firstPassengerIdx]    # 每辆车上的乘客
            keypointDistVec[firstPassengerIdx] = 0  # 找到后进行虚拟删除，将值赋为0
            while numPassenger < CARSEATS:
                # Searching next passenger
                # ----------------------------
                # find the passengers in the neighborhood area, remove the previous arranged passenger location
                neighborhoodIdxVec1 = auxfn.getNeighborhoodIdx(orderVec, orderVec[firstPassengerIdx, :], SEARCHRADIUS)
                neighborhoodIdxVec = [x for x in neighborhoodIdxVec1 if x not in arrangedPassengerIdx]
                # ----------------------------
                # if there is someone in the neighborhood， choose that one as next passenger
                # else if there is no unarranged passenger in the neighborhood, search all the rest of points
                # choose the closest point && closer to key point than current passenger
                if len(neighborhoodIdxVec) >= 1:
                    nextPassengerIdx = neighborhoodIdxVec
                else:
                    ix = np.where(np.in1d(np.arange(orderNum), arrangedPassengerIdx, invert=True))
                    if len(ix[0]) is 0:   # 最后一个人直接上车
                        numPassengerVec.append(numPassenger)
                        time2AirportVec.append(currentScheduleVec)
                        currentScheduleVec = []
                        break
                    else:
                        tmpnextPassengerIdx = auxfn.getSortedPointIdx(orderVec[ix[0], :], orderVec[firstPassengerIdx, :])
                        nextPassengerIdx = [ix[0][y] for y in tmpnextPassengerIdx]
                # 周围没有人了结束循环叫新车
                if len(nextPassengerIdx) is 0:
                    numPassengerVec.append(numPassenger)
                    time2AirportVec.append(currentScheduleVec)
                    currentScheduleVec = []
                    break
                else:
                    # 车上没有6个人，周围有人，但是周围上车后车上最小的人数都大于6就结束循环叫新车或是最小的时间都大于限制
                    # 时间限制暂时没有写（后面加上速度后补上）
                    neighborGetOnCar = [seatNumVec[element] for element in nextPassengerIdx]
                    carseatsWithNeighbor = np.array(neighborGetOnCar) + numPassenger
                    if carseatsWithNeighbor.min() > CARSEATS:
                        numPassengerVec.append(numPassenger)
                        time2AirportVec.append(currentScheduleVec)
                        currentScheduleVec = []
                        break
                # compute the driving time from current to the next passenger
                for i in xrange(len(nextPassengerIdx)):
                    if (numPassenger + seatNumVec[nextPassengerIdx[i]]) > CARSEATS:
                        continue
                    elif (dis.checkTimeLimitCondition(TIMELIMIT, orderVec[firstPassengerIdx, :],
                                                      orderVec[nextPassengerIdx[i], :], AMAPAIRPORTCOORDINATE, currentScheduleVec)):
                        numPassenger += seatNumVec[nextPassengerIdx[i]]
                        arrangedPassengerIdx.append(nextPassengerIdx[i])
                        firstPassengerIdx = nextPassengerIdx[i]
                        keypointDistVec[firstPassengerIdx] = 0
                        break
            else:
                # 车上有6个人就结束循环叫新车
                numPassengerVec.append(numPassenger)
                time2AirportVec.append(currentScheduleVec)
                currentScheduleVec = []
        # 获取每辆车的地点的下标[[],[]]二维列表
        carList = dis.getCarPassengerList(time2AirportVec, arrangedPassengerIdx)
        # 获取每个地点的订单号[[[],[],[]],[[],[],[],[]]]二维列表
        carOrderList = dis.getThePassengerOrderForEachCar(carList, RMMTSixpassengerOrderID)
        # 获取每个订单到机场的时间[[[],[],[]],[]]二维列表
        carOrderAndTimeList = dis.getOrderAndTimeInfos(carOrderList, time2AirportVec)
        if len(getonthecarLoc) is 0:
            # 如果没有已经上车的订单就封装成json数组
            AllCarOrderAndTime = copy.copy(carOrderAndTimeList)
        else:
            # 如果有已经上车的订单就将两个列表相加
            hasgetonthecarLocandTime = dis.gethasgotonthecartimedistance(getonthecarLoc, getonthecar)
            AllCarOrderAndTime = carOrderAndTimeList+hasgetonthecarLocandTime
        # jsondata = dis.incodejs(AllCarOrderAndTime)
        return AllCarOrderAndTime
    else:
        hasgetonthecarLocandTime = dis.gethasgotonthecartimedistance(getonthecarLoc, getonthecar)
        car = []
        for element in RMMTSixpassengerOrderID[0]:
            tmp = []
            tmp.append(element)
            tmp.append(0)
            car.append(tmp)
        carOrderAndTimeList = [car]
        AllCarOrderAndTime = carOrderAndTimeList + hasgetonthecarLocandTime
        return AllCarOrderAndTime

# event.set()



