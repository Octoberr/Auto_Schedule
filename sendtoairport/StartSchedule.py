# coding:utf-8

"""
Donghui Chen, Wangmeng Song
May 15, 2017
排班逻辑修改 Wangmeng Song
June 20, 2017
June 29, 2017
June 30, 2017
添加新逻辑
July 21,2017
增加新逻辑
August 8,2017
优化人少
"""

import numpy as np
import copy
from compiler.ast import flatten

import schedule
import mapAPI
import auxfn
from recomTimeOnTheBus import eastandwestside

AMAPKEYCOORDINATE = [30.599403, 104.040368]  # 高速交汇点
AMAPAIRPORTCOORDINATE = [30.574590, 103.955020]  # 成都机场
TIANFUSQUIRE = [30.604043, 104.074086]
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
    area = eastandwestside.SIDE()  # 实例化区分区域的类
    # 获得两个list，specifyDriverDic, normalPassengerDic
    specifyDriverDic = []  # 存储指定司机的乘客
    normalPassengerDic = []  # 存储普通乘客
    dis.getTheSpecifyAndNormal(specifyDriverDic, normalPassengerDic, resdict)
    # 将数据赋予一个东边和西边的属性，并且将2.5环外的订单直接上车
    arrangedPassengerIdx = []  # store order index on all cars
    currentScheduleVec = []  # temporary using, store each passenger's travelling time on the same car
    currentPassengerIdx = []  # 存储当前车的乘客
    time2AirportVec = []  # store each passenger's travelling time
    numPassengerVec = []  # store the number of passengers on each car
    # ------------------
    # Get all the order coordinates, save in a 2D-array, 1st row is latitude, 2nd row is longitude
    getonthecar = []  # [[A,,B,C],[D,E,F]] 存储一个满足条件上车的或者乘客==5or6的订单
    getonthecarLoc = []  # [(lat1,lng1),(lat2,lng2)] 存储一个地点的lat,lng
    getonthecarseatnum = []  # [[1,2,3],[2,3]] 存储一个地点的乘客人数
    repeatpoid = []     # 存储第一次处理的传入数据的订单号
    repeatloc = []      # 存储第一次处理的传入数据的经纬度
    repeatseatnum = []      # 存储第一次处理的传入数据的乘客人数
    # 处理第一次传入的数据，第一次处理：过滤一个订单乘客人数==5or6
    # 待修改（一个订单==5或者一个订单==6直接上车，或者在2.5环外直接上车，修改待确认）
    dis.getAllRepeatData(repeatpoid, repeatloc, repeatseatnum, getonthecar, getonthecarLoc, getonthecarseatnum, normalPassengerDic)
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
    if len(getonthecarLoc) > 0:
        # 寻找一个地点乘客人数==5的周围是否存在1个订单1个人的情况
        dis.getTheFivePersonAroundOnlyOne(getonthecar, getonthecarLoc, getonthecarseatnum,
                                          RMMTSixpassengerOrderID, RMMTSixpassengerLoc, RMMTSixpassengerseatnum)
    # 判断loc是否在纬度以北，如果在纬度以南就直接上车，纬度以北进入排班
    northOrderID = []   # [[A,,B,C],[D,E,F]]
    northOrderLoc = []  # [(lat1,lng1),(lat2,lng2)]
    northOrderSeatnum = []  # [[1,2,3],[2,3]]
    # 第四次处理超过处理范围的南边的订单将不去接送
    dis.distinguish(getonthecar, getonthecarLoc, getonthecarseatnum, RMMTSixpassengerOrderID, RMMTSixpassengerLoc, RMMTSixpassengerseatnum, northOrderID, northOrderLoc, northOrderSeatnum)
    # 处理指定司机的订单
    if len(specifyDriverDic) > 0:
        specifyDriverOrder = dis.getTheSpecifyDriverOrder(northOrderID, northOrderLoc, northOrderSeatnum, specifyDriverDic)
    # 进入调用schedule的订单数
    orderNum = len(northOrderLoc)     # 进入排班算法的总地点数
    seatNumVec = dis.getOrderNumVec(northOrderSeatnum)  # 二维的乘客人数转换为与地点对应的一维数组 array[3,1]
    sidevec = area.ateast(northOrderLoc, orderNum)   # 地区东边和西边的代码，地图东为1，西为2,array
    eastareaVec = np.where(sidevec <= 1)[0]  # 东边地区的index集合，一维array
    westareaVec = np.where(sidevec >= 2)[0]  # 西边地区的index集合，一维array
    # 如果两边小于等于就直接上车
    # if sum(seatNumVec) <= 1:
    #     dis.leftandrightgetonthecar(getonthecar, northOrderID, northOrderLoc)
    #     if len(specifyDriverDic) > 0:
    #         AllCarOrder = getonthecar + specifyDriverOrder
    #     else:
    #         AllCarOrder = getonthecar
    #     return AllCarOrder
    # 如果东边和西边的人数同时小于或等于6就分别上车
    if sum(seatNumVec[eastareaVec]) <= 6 and sum(seatNumVec[westareaVec]) <= 6:
        eastcar = [northOrderID[e] for e in eastareaVec]
        if len(eastcar) > 0:
            eastloc = [northOrderLoc[lc] for lc in eastareaVec]
            eastcarpool = [ewd for (elc, ewd) in sorted(zip([elat[0] for elat in eastloc], eastcar), reverse=True)]
            getonthecar.append(flatten(eastcarpool))
        westcar = [northOrderID[w] for w in westareaVec]
        if len(westcar) > 0:
            westloc = [northOrderLoc[wl] for wl in westareaVec]
            westcarpool = [wd for (lc, wd) in sorted(zip([lat[0] for lat in westloc], westcar), reverse=True)]
            getonthecar.append(flatten(westcarpool))
        if len(specifyDriverDic) > 0:
            AllCarOrder = getonthecar + specifyDriverOrder
        else:
            AllCarOrder = copy.copy(getonthecar)
        return AllCarOrder
    # 如果东边小于等于6，西边大于6,东边上车
    elif sum(seatNumVec[eastareaVec]) <= 6 and sum(seatNumVec[westareaVec]) > 6:
        eastcar = [northOrderID[e] for e in eastareaVec]
        if len(eastcar) > 0:
            eastloc = [northOrderLoc[f] for f in eastareaVec]
            carpool = [wd for (lc, wd) in sorted(zip([lat[0] for lat in eastloc], eastcar), reverse=True)]
            getonthecar.append(flatten(carpool))
            for delindex in reversed(eastareaVec):
                del(northOrderID[delindex])
                del(northOrderLoc[delindex])
                del(northOrderSeatnum[delindex])
        restorderNo = []  # [[A,,B,C],[D,E,F]]
        restorderLoc = []  # [(lat1,lng1),(lat2,lng2)]
        restorderSeatNo = []  # [[1,2,3],[2,3]]
        newwestareaVec = np.arange(len(northOrderLoc))
        dis.westschedule(northOrderID, northOrderLoc, northOrderSeatnum, newwestareaVec, restorderNo, restorderLoc,
                         restorderSeatNo, getonthecar)
        if len(restorderLoc) > 1:
            restorderNum = len(restorderLoc)
            restsideVec = area.ateast(restorderLoc, restorderNum)  # 地区东边和西边的代码，地图东为1，西为2,array
            restSeatNoVec = dis.getOrderNumVec(restorderSeatNo)  # 二维的乘客人数转换为与地点对应的一维数组 array[3,1]
            orderVec = dis.getOrderLocVec(restorderLoc)  # 一维的经纬度列表转换为二维的经纬度数组
            keypointDistVec = auxfn.calcDistVec(TIANFUSQUIRE, orderVec)  # 获取每个地点到天府高速交汇点的一维数组
            # Calculate the time distance from airport for each order
            airportTimeDistVec = GTI.getTimeDistVec(AMAPAIRPORTCOORDINATE, orderVec, restorderNum)  # 获取每个地点到机场的时间距离
            while len(arrangedPassengerIdx) < restorderNum:
                firstPassengerIdx = np.argmax(keypointDistVec)  # 寻找距离机场最远的第一个上车的人
                arrangedPassengerIdx.append(firstPassengerIdx)  # 存储地点位置的索引[3,4,1,0]
                currentScheduleVec.append(airportTimeDistVec[firstPassengerIdx])  # 存储时间的索引，2017/6/19时间已经不再使用
                currentPassengerIdx.append(firstPassengerIdx)
                numPassenger = restSeatNoVec[firstPassengerIdx]  # 每辆车上的乘客
                keypointDistVec[firstPassengerIdx] = 0  # 找到后进行虚拟删除，将值赋为0
                while numPassenger < CARSEATS:
                    # Searching next passenger
                    # ----------------------------
                    # find the passengers in the neighborhood area, remove the previous arranged passenger location
                    # 当前点side为1可以选择所有的点找周围的点，当前点为2就只能找2
                    neighborhoodIdxVec1 = auxfn.getNeighborhoodIdx(orderVec, orderVec[firstPassengerIdx, :],
                                                                   SEARCHRADIUS, firstPassengerIdx, restsideVec)
                    neighborhoodIdxVec = [x for x in neighborhoodIdxVec1 if x not in arrangedPassengerIdx]
                    # ----------------------------
                    # if there is someone in the neighborhood， choose that one as next passenger
                    # else if there is no unarranged passenger in the neighborhood, search all the rest of points
                    # choose the closest point && closer to key point than current passenger
                    if len(neighborhoodIdxVec) >= 1:
                        nextPassengerIdx = dis.checkLongdiscondition(currentPassengerIdx, restorderLoc,
                                                                     neighborhoodIdxVec)
                    else:
                        ix = np.where(np.in1d(np.arange(restorderNum), arrangedPassengerIdx, invert=True))
                        if len(ix[0]) == 0:  # 最后一个人直接上车
                            numPassengerVec.append(numPassenger)
                            time2AirportVec.append(currentScheduleVec)
                            currentScheduleVec = []
                            break
                        else:
                            # 当前点side为1可以选择所有的点找周围的点，当前点为2就只能找2
                            currentside = restsideVec[firstPassengerIdx]
                            tmpnextPassengerIdx = auxfn.getSortedPointIdx(orderVec[ix[0], :],
                                                                          orderVec[firstPassengerIdx, :],
                                                                          restsideVec[ix[0]], currentside)
                            tmpPassengerIdx = [ix[0][y] for y in tmpnextPassengerIdx]
                            nextPassengerIdx = dis.checkLongdiscondition(currentPassengerIdx, restorderLoc,
                                                                         tmpPassengerIdx)
                    # 周围没有人了结束循环叫新车
                    if len(nextPassengerIdx) == 0:
                        numPassengerVec.append(numPassenger)
                        time2AirportVec.append(currentScheduleVec)
                        currentScheduleVec = []
                        currentPassengerIdx = []
                        break
                    else:
                        # 车上没有6个人，周围有人，但是周围上车后车上最小的人数都大于6就结束循环叫新车或是最小的时间都大于限制
                        # 时间限制暂时没有写（后面加上速度后补上）
                        neighborGetOnCar = [restSeatNoVec[element] for element in nextPassengerIdx]
                        carseatsWithNeighbor = np.array(neighborGetOnCar) + numPassenger
                        if carseatsWithNeighbor.min() > CARSEATS:
                            numPassengerVec.append(numPassenger)
                            time2AirportVec.append(currentScheduleVec)
                            currentScheduleVec = []
                            currentPassengerIdx = []
                            break
                    # compute the driving time from current to the next passenger
                    for i in xrange(len(nextPassengerIdx)):
                        if (numPassenger + restSeatNoVec[nextPassengerIdx[i]]) > CARSEATS:
                            continue
                        elif (dis.checkTimeLimitCondition(TIMELIMIT, orderVec[firstPassengerIdx, :],
                                                          orderVec[nextPassengerIdx[i], :], AMAPAIRPORTCOORDINATE,
                                                          currentScheduleVec, currentPassengerIdx,
                                                          nextPassengerIdx[i])):
                            numPassenger += restSeatNoVec[nextPassengerIdx[i]]
                            arrangedPassengerIdx.append(nextPassengerIdx[i])
                            firstPassengerIdx = nextPassengerIdx[i]
                            keypointDistVec[firstPassengerIdx] = 0
                            break
                else:
                    # 车上有6个人就结束循环叫新车
                    numPassengerVec.append(numPassenger)
                    time2AirportVec.append(currentScheduleVec)
                    currentScheduleVec = []
                    currentPassengerIdx = []
            # 获取每辆车的地点的下标[[],[]]二维列表
            carList = dis.getCarPassengerList(time2AirportVec, arrangedPassengerIdx)
            # 对获取结果排序 f**k
            # sortcarList = dis.sortPassenger(carList, northOrderLoc)
            # 获取每个地点的订单号[[a,b,c],[d,c,e]]二维列表
            carOrderList = dis.getThePassengerOrderForEachCar(carList, restorderNo)
            # 获取每个订单到机场的时间[[[],[],[]],[]]二维列表
            # carOrderAndTimeList = dis.getOrderAndTimeInfos(carOrderList, time2AirportVec)
            if len(specifyDriverDic) == 0:
                AllCarOrder = carOrderList + getonthecar  # [[a,v,s],[q,w,e,r,f]]
                return AllCarOrder
            else:
                AllCarOrder = carOrderList + getonthecar + specifyDriverOrder
                return AllCarOrder
        else:
            if len(restorderNo) == 1:
                getonthecar.append(restorderNo[0])
            if len(specifyDriverDic) == 0:
                AllCarOrder = copy.copy(getonthecar)  # [[a,v,s],[q,w,e,r,f]]
                return AllCarOrder
            else:
                AllCarOrder = getonthecar + specifyDriverOrder
                return AllCarOrder
    # 如果西边小于等于6，东边大于6
    elif sum(seatNumVec[eastareaVec]) > 6 and sum(seatNumVec[westareaVec]) <= 6:
        westcar = [northOrderID[w] for w in westareaVec]
        if len(westcar) > 0:
            westloc = [northOrderLoc[g] for g in westareaVec]
            carpool = [wd for (lc, wd) in sorted(zip([lat[0] for lat in westloc], westcar), reverse=True)]
            getonthecar.append(flatten(carpool))
            for delindex in reversed(westareaVec):
                del(northOrderID[delindex])
                del(northOrderLoc[delindex])
                del(northOrderSeatnum[delindex])
        restorderNum = len(northOrderLoc)
        restsideVec = area.ateast(northOrderLoc, restorderNum)  # 地区东边和西边的代码，地图东为1，西为2,array
        restSeatNoVec = dis.getOrderNumVec(northOrderSeatnum)  # 二维的乘客人数转换为与地点对应的一维数组 array[3,1]
        orderVec = dis.getOrderLocVec(northOrderLoc)  # 一维的经纬度列表转换为二维的经纬度数组
        keypointDistVec = auxfn.calcDistVec(TIANFUSQUIRE, orderVec)  # 获取每个地点到天府高速交汇点的一维数组
        # Calculate the time distance from airport for each order
        airportTimeDistVec = GTI.getTimeDistVec(AMAPAIRPORTCOORDINATE, orderVec, restorderNum)  # 获取每个地点到机场的时间距离
        while len(arrangedPassengerIdx) < restorderNum:
            firstPassengerIdx = np.argmax(keypointDistVec)  # 寻找距离机场最远的第一个上车的人
            arrangedPassengerIdx.append(firstPassengerIdx)  # 存储地点位置的索引[3,4,1,0]
            currentScheduleVec.append(airportTimeDistVec[firstPassengerIdx])  # 存储时间的索引，2017/6/19时间已经不再使用
            currentPassengerIdx.append(firstPassengerIdx)
            numPassenger = restSeatNoVec[firstPassengerIdx]  # 每辆车上的乘客
            keypointDistVec[firstPassengerIdx] = 0  # 找到后进行虚拟删除，将值赋为0
            while numPassenger < CARSEATS:
                # Searching next passenger
                # ----------------------------
                # find the passengers in the neighborhood area, remove the previous arranged passenger location
                # 当前点side为1可以选择所有的点找周围的点，当前点为2就只能找2
                neighborhoodIdxVec1 = auxfn.getNeighborhoodIdx(orderVec, orderVec[firstPassengerIdx, :], SEARCHRADIUS,
                                                               firstPassengerIdx, restsideVec)
                neighborhoodIdxVec = [x for x in neighborhoodIdxVec1 if x not in arrangedPassengerIdx]
                # ----------------------------
                # if there is someone in the neighborhood， choose that one as next passenger
                # else if there is no unarranged passenger in the neighborhood, search all the rest of points
                # choose the closest point && closer to key point than current passenger
                if len(neighborhoodIdxVec) >= 1:
                    nextPassengerIdx = dis.checkLongdiscondition(currentPassengerIdx, northOrderLoc, neighborhoodIdxVec)
                else:
                    ix = np.where(np.in1d(np.arange(restorderNum), arrangedPassengerIdx, invert=True))
                    if len(ix[0]) == 0:  # 最后一个人直接上车
                        numPassengerVec.append(numPassenger)
                        time2AirportVec.append(currentScheduleVec)
                        currentScheduleVec = []
                        break
                    else:
                        # 当前点side为1可以选择所有的点找周围的点，当前点为2就只能找2
                        currentside = restsideVec[firstPassengerIdx]
                        tmpnextPassengerIdx = auxfn.getSortedPointIdx(orderVec[ix[0], :],
                                                                      orderVec[firstPassengerIdx, :],
                                                                      restsideVec[ix[0]], currentside)
                        tmpPassengerIdx = [ix[0][y] for y in tmpnextPassengerIdx]
                        nextPassengerIdx = dis.checkLongdiscondition(currentPassengerIdx, northOrderLoc, tmpPassengerIdx)
                # 周围没有人了结束循环叫新车
                if len(nextPassengerIdx) == 0:
                    numPassengerVec.append(numPassenger)
                    time2AirportVec.append(currentScheduleVec)
                    currentScheduleVec = []
                    currentPassengerIdx = []
                    break
                else:
                    # 车上没有6个人，周围有人，但是周围上车后车上最小的人数都大于6就结束循环叫新车或是最小的时间都大于限制
                    # 时间限制暂时没有写（后面加上速度后补上）
                    neighborGetOnCar = [restSeatNoVec[element] for element in nextPassengerIdx]
                    carseatsWithNeighbor = np.array(neighborGetOnCar) + numPassenger
                    if carseatsWithNeighbor.min() > CARSEATS:
                        numPassengerVec.append(numPassenger)
                        time2AirportVec.append(currentScheduleVec)
                        currentScheduleVec = []
                        currentPassengerIdx = []
                        break
                # compute the driving time from current to the next passenger
                for i in xrange(len(nextPassengerIdx)):
                    if (numPassenger + restSeatNoVec[nextPassengerIdx[i]]) > CARSEATS:
                        continue
                    elif (dis.checkTimeLimitCondition(TIMELIMIT, orderVec[firstPassengerIdx, :],
                                                      orderVec[nextPassengerIdx[i], :], AMAPAIRPORTCOORDINATE,
                                                      currentScheduleVec, currentPassengerIdx, nextPassengerIdx[i])):
                        numPassenger += restSeatNoVec[nextPassengerIdx[i]]
                        arrangedPassengerIdx.append(nextPassengerIdx[i])
                        firstPassengerIdx = nextPassengerIdx[i]
                        keypointDistVec[firstPassengerIdx] = 0
                        break
            else:
                # 车上有6个人就结束循环叫新车
                numPassengerVec.append(numPassenger)
                time2AirportVec.append(currentScheduleVec)
                currentScheduleVec = []
                currentPassengerIdx = []
        # 获取每辆车的地点的下标[[],[]]二维列表
        carList = dis.getCarPassengerList(time2AirportVec, arrangedPassengerIdx)
        # 对获取结果排序 f**k
        # sortcarList = dis.sortPassenger(carList, northOrderLoc)
        # 获取每个地点的订单号[[a,b,c],[d,c,e]]二维列表
        carOrderList = dis.getThePassengerOrderForEachCar(carList, northOrderID)
        # 获取每个订单到机场的时间[[[],[],[]],[]]二维列表
        # carOrderAndTimeList = dis.getOrderAndTimeInfos(carOrderList, time2AirportVec)
        if len(specifyDriverDic) == 0:
            # hasgetonthecarLocandTime = dis.gethasgotonthecartimedistance(getonthecarLoc, getonthecar)
            AllCarOrder = carOrderList + getonthecar  # [[a,v,s],[q,w,e,r,f]]
            # jsondata = dis.incodejs(AllCarOrderAndTime)
            return AllCarOrder
        else:
            AllCarOrder = carOrderList + getonthecar + specifyDriverOrder
            return AllCarOrder

    else:
        # 对订单在西边2环到2.5环的情况进行排班
        restorderNo = []   # [[A,,B,C],[D,E,F]]
        restorderLoc = []   # [(lat1,lng1),(lat2,lng2)]
        restorderSeatNo = []    # [[1,2,3],[2,3]]
        dis.westschedule(northOrderID, northOrderLoc, northOrderSeatnum, westareaVec, restorderNo, restorderLoc, restorderSeatNo, getonthecar)
        # 排班开始
        restorderNum = len(restorderLoc)
        restsideVec = area.ateast(restorderLoc, restorderNum)   # 地区东边和西边的代码，地图东为1，西为2,array
        restSeatNoVec = dis.getOrderNumVec(restorderSeatNo)  # 二维的乘客人数转换为与地点对应的一维数组 array[3,1]
        orderVec = dis.getOrderLocVec(restorderLoc)     # 一维的经纬度列表转换为二维的经纬度数组
        keypointDistVec = auxfn.calcDistVec(TIANFUSQUIRE, orderVec)    # 获取每个地点到天府高速交汇点的一维数组
        # Calculate the time distance from airport for each order
        airportTimeDistVec = GTI.getTimeDistVec(AMAPAIRPORTCOORDINATE, orderVec, restorderNum)  # 获取每个地点到机场的时间距离
        while len(arrangedPassengerIdx) < restorderNum:
            firstPassengerIdx = np.argmax(keypointDistVec)  # 寻找距离机场最远的第一个上车的人
            arrangedPassengerIdx.append(firstPassengerIdx)  # 存储地点位置的索引[3,4,1,0]
            currentScheduleVec.append(airportTimeDistVec[firstPassengerIdx])  # 存储时间的索引，2017/6/19时间已经不再使用
            currentPassengerIdx.append(firstPassengerIdx)
            numPassenger = restSeatNoVec[firstPassengerIdx]    # 每辆车上的乘客
            keypointDistVec[firstPassengerIdx] = 0  # 找到后进行虚拟删除，将值赋为0
            while numPassenger < CARSEATS:
                # Searching next passenger
                # ----------------------------
                # find the passengers in the neighborhood area, remove the previous arranged passenger location
                # 当前点side为1可以选择所有的点找周围的点，当前点为2就只能找2
                neighborhoodIdxVec1 = auxfn.getNeighborhoodIdx(orderVec, orderVec[firstPassengerIdx, :], SEARCHRADIUS, firstPassengerIdx, restsideVec)
                neighborhoodIdxVec = [x for x in neighborhoodIdxVec1 if x not in arrangedPassengerIdx]
                # ----------------------------
                # if there is someone in the neighborhood， choose that one as next passenger
                # else if there is no unarranged passenger in the neighborhood, search all the rest of points
                # choose the closest point && closer to key point than current passenger
                if len(neighborhoodIdxVec) >= 1:
                    nextPassengerIdx = dis.checkLongdiscondition(currentPassengerIdx, restorderLoc, neighborhoodIdxVec)
                else:
                    ix = np.where(np.in1d(np.arange(restorderNum), arrangedPassengerIdx, invert=True))
                    if len(ix[0]) == 0:   # 最后一个人直接上车
                        numPassengerVec.append(numPassenger)
                        time2AirportVec.append(currentScheduleVec)
                        currentScheduleVec = []
                        break
                    else:
                        # 当前点side为1可以选择所有的点找周围的点，当前点为2就只能找2
                        currentside = restsideVec[firstPassengerIdx]
                        tmpnextPassengerIdx = auxfn.getSortedPointIdx(orderVec[ix[0], :], orderVec[firstPassengerIdx, :], restsideVec[ix[0]], currentside)
                        tmpPassengerIdx = [ix[0][y] for y in tmpnextPassengerIdx]
                        nextPassengerIdx = dis.checkLongdiscondition(currentPassengerIdx, restorderLoc, tmpPassengerIdx)
                # 周围没有人了结束循环叫新车
                if len(nextPassengerIdx) == 0:
                    numPassengerVec.append(numPassenger)
                    time2AirportVec.append(currentScheduleVec)
                    currentScheduleVec = []
                    currentPassengerIdx = []
                    break
                else:
                    # 车上没有6个人，周围有人，但是周围上车后车上最小的人数都大于6就结束循环叫新车或是最小的时间都大于限制
                    # 时间限制暂时没有写（后面加上速度后补上）
                    neighborGetOnCar = [restSeatNoVec[element] for element in nextPassengerIdx]
                    carseatsWithNeighbor = np.array(neighborGetOnCar) + numPassenger
                    if carseatsWithNeighbor.min() > CARSEATS:
                        numPassengerVec.append(numPassenger)
                        time2AirportVec.append(currentScheduleVec)
                        currentScheduleVec = []
                        currentPassengerIdx = []
                        break
                # compute the driving time from current to the next passenger
                for i in xrange(len(nextPassengerIdx)):
                    if (numPassenger + restSeatNoVec[nextPassengerIdx[i]]) > CARSEATS:
                        continue
                    elif (dis.checkTimeLimitCondition(TIMELIMIT, orderVec[firstPassengerIdx, :],
                                                      orderVec[nextPassengerIdx[i], :], AMAPAIRPORTCOORDINATE, currentScheduleVec, currentPassengerIdx, nextPassengerIdx[i])):
                        numPassenger += restSeatNoVec[nextPassengerIdx[i]]
                        arrangedPassengerIdx.append(nextPassengerIdx[i])
                        firstPassengerIdx = nextPassengerIdx[i]
                        keypointDistVec[firstPassengerIdx] = 0
                        break
            else:
                # 车上有6个人就结束循环叫新车
                numPassengerVec.append(numPassenger)
                time2AirportVec.append(currentScheduleVec)
                currentScheduleVec = []
                currentPassengerIdx = []
        # 获取每辆车的地点的下标[[],[]]二维列表
        carList = dis.getCarPassengerList(time2AirportVec, arrangedPassengerIdx)
        # 对获取结果排序 f**k
        # sortcarList = dis.sortPassenger(carList, northOrderLoc)
        # 获取每个地点的订单号[[a,b,c],[d,c,e]]二维列表
        carOrderList = dis.getThePassengerOrderForEachCar(carList, restorderNo)
        # 获取每个订单到机场的时间[[[],[],[]],[]]二维列表
        # carOrderAndTimeList = dis.getOrderAndTimeInfos(carOrderList, time2AirportVec)
        if len(specifyDriverDic) == 0:
            if len(getonthecar) == 0:
                # 如果没有已经上车的订单就封装成json数组
                AllCarOrder = copy.copy(carOrderList)
            else:
                # 如果有已经上车的订单就将两个列表相加
                # hasgetonthecarLocandTime = dis.gethasgotonthecartimedistance(getonthecarLoc, getonthecar)
                AllCarOrder = carOrderList + getonthecar  # [[a,v,s],[q,w,e,r,f]]
            # jsondata = dis.incodejs(AllCarOrderAndTime)
            return AllCarOrder
        else:
            if len(getonthecar) == 0:
                AllCarOrder = carOrderList + specifyDriverOrder
            else:
                AllCarOrder = carOrderList + getonthecar + specifyDriverOrder
            return AllCarOrder
# event.set()



