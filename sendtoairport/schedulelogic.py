# coding:utf-8

"""
math logic
create by swm
september 18, 2017
"""
# 外部引用
import numpy as np
# 内部引用
from recomTimeOnTheBus import getneighbor
from recomTimeOnTheBus import eastandwestside
import schedule
import auxfn
# 预定区域每个区域相邻的区域
area1 = [3, 1, 2, 6]
area2 = [0, 2, 12, 7, 3, 27]
area3 = [0, 1, 27]
area4 = [6, 0, 1, 7, 4]
area5 = [5, 6, 3, 7, 8, 9]
area6 = [6, 4, 8, 9, 17, 3]
area7 = [0, 3, 4, 5, 16, 17]
area8 = [3, 1, 12, 11, 8, 4]
area9 = [4, 3, 7, 12, 11, 10, 9, 5]
area10 = [5, 4, 8, 10, 18, 17, 20]
area11 = [9, 11, 15, 20, 8, 22, 18]
area12 = [8, 12, 15, 10, 9, 7, 13]
area13 = [7, 1, 13, 11, 8, 15]
area14 = [12, 14, 15, 27, 11]
area15 = [13, 15, 24, 27, 22]
area16 = [10, 11, 13, 14, 22, 20, 12, 24]
area17 = [6, 17, 19, 25, 5]
area18 = [16, 5, 9, 18, 6, 19]
area19 = [17, 9, 20, 19, 16, 10, 21]
area20 = [16, 18, 21, 25, 17, 20]
area21 = [18, 10, 21, 19, 9, 15, 23]
area22 = [19, 20, 23, 25, 18, 22]
area23 = [20, 15, 24, 23, 21, 10, 14]
area24 = [21, 22, 24, 25, 20]
area25 = [22, 14, 23, 25, 15, 26, 27]
area26 = [16, 19, 21, 23, 26, 24]
area27 = [25, 24, 27, 23, 14]
area28 = [14, 13, 1, 2, 24, 26]
areaneighbor = [area1, area2, area3, area4, area5, area6, area7, area8, area9, area10, area11, area12,
                area13, area14, area15, area16, area17, area18, area19, area20, area21, area22, area23,
                area24, area25, area26, area27, area28]
TIANFUSQUIRE = [30.604043, 104.074086]
CARSEATS = 6     # 一辆车最大乘客为6个人
fivecarset = 5   # 5个人上车也可以
SEARCHRADIUS = 1500  # 1500m的范围
EastSpecificList = [3, 7, 12, 13, 14]
WestSpecificList = [19, 21, 23]


def getrestlist(currentarea):
    if currentarea in EastSpecificList:
        areadist = len(EastSpecificList)
        currentindex = EastSpecificList.index(currentarea)
        restarea = [EastSpecificList[i] for i in range(currentindex, areadist)]
        return restarea
    else:
        areadist = len(WestSpecificList)
        currentindex = WestSpecificList.index(currentarea)
        restarea = [WestSpecificList[i] for i in range(currentindex, areadist)]
        return restarea


def slogic(restorderNo, restorderLoc, restorderSeatNo):
    arealoclist = []  # 每个idx对应的区域范围
    for loc in restorderLoc:
        areanum = getneighbor.findtheareanumber(loc[0], loc[1])
        arealoclist.append(areanum)
    restorderNum = len(restorderLoc)
    area = eastandwestside.SIDE()  # 实例化区分区域的类
    restsideVec = area.ateast(restorderNum, arealoclist)  # 地区东边和西边的代码，地图东为1，西为2,array
    dis = schedule.DIST()   # 实例化DIST类
    restSeatNoVec = dis.getOrderNumVec(restorderSeatNo)  # 二维的乘客人数转换为与地点对应的一维数组 array[3,1]
    orderVec = dis.getOrderLocVec(restorderLoc)  # 一维的经纬度列表转换为二维的经纬度数组
    keypointDistVec = auxfn.calcDistVec(TIANFUSQUIRE, orderVec)  # 获取每个地点到天府高速交汇点的一维数组
    allgetonthecaridx = []   # 已经上车的订单的idx
    carorder = []  # 存储上车的订单bid的index
    while len(allgetonthecaridx) < restorderNum:
        # 寻找一辆车的第一个人
        tmpcarorder = []  # 存储一辆车的订单
        firstPassengerIdx = np.argmax(keypointDistVec)  # 寻找距离机场最远的第一个上车的人
        allgetonthecaridx.append(firstPassengerIdx)    # 存储所有已经上车的idx
        tmpcarorder.append(firstPassengerIdx)
        numPassenger = restSeatNoVec[firstPassengerIdx]  # 一辆车上的乘客数量
        keypointDistVec[firstPassengerIdx] = 0  # 找到后进行虚拟删除，将值赋为0
        while numPassenger < CARSEATS:
            # 获得当前点所在的区域
            currentarea = arealoclist[firstPassengerIdx]
            if currentarea in EastSpecificList+WestSpecificList:
                # 寻找当前区域，然后寻找临近区域
                # 获取当前剩下的区域
                therestlist = getrestlist(currentarea)
                for area in therestlist:
                    # 获取当前区域的所有点
                    sameareaindx = dis.getthesameareapointdistance(arealoclist, firstPassengerIdx, area,
                                                                   allgetonthecaridx, restorderLoc)
                    if sameareaindx is not None:
                        for sameidx in sameareaindx:
                            if numPassenger + restSeatNoVec[sameidx] <= CARSEATS:
                                allgetonthecaridx.append(sameidx)
                                tmpcarorder.append(sameidx)
                                numPassenger += restSeatNoVec[sameidx]
                                keypointDistVec[sameidx] = 0
                                firstPassengerIdx = sameidx
                                if numPassenger == CARSEATS:
                                    break  # 结束循环
                    if numPassenger == fivecarset or numPassenger == CARSEATS:
                        # 当前区域的人找完后满足5人或者6人，说明人找齐了
                        break
                    else:
                        # 当前区域的人数不够先寻找距离本区域边界只有100m的点
                        neighborareaidx = getneighbor.theneighborarea(arealoclist, allgetonthecaridx, area,
                                                                      restorderLoc, areaneighbor[area])
                        if neighborareaidx is not None:
                            for neighidx in neighborareaidx:
                                if numPassenger + restSeatNoVec[neighidx] <= CARSEATS:
                                    allgetonthecaridx.append(neighidx)
                                    tmpcarorder.append(neighidx)
                                    numPassenger += restSeatNoVec[neighidx]
                                    keypointDistVec[neighidx] = 0
                                    if numPassenger == CARSEATS:
                                        break  # 结束循环
                         # 当满足一辆车上车的人就上车打破循环
                        if numPassenger == fivecarset or numPassenger == CARSEATS:
                            # 当前区域的人找完后满足5人或者6人，说明人找齐了
                            break
            else:
                # 直接寻找当前区域和临近区域，当前一个区域
                # 1、相同区域,依据到当前点的距离排序的index
                sameareaindx = dis.getthesameareapointdistance(arealoclist, firstPassengerIdx, currentarea, allgetonthecaridx, restorderLoc)
                if sameareaindx is not None:
                    for sameidx in sameareaindx:
                        if numPassenger + restSeatNoVec[sameidx] <= CARSEATS:
                            allgetonthecaridx.append(sameidx)
                            tmpcarorder.append(sameidx)
                            numPassenger += restSeatNoVec[sameidx]
                            keypointDistVec[sameidx] = 0
                            firstPassengerIdx = sameidx
                            if numPassenger == CARSEATS:
                                break  # 结束循环
                    if numPassenger == fivecarset or numPassenger == CARSEATS:
                        # 当前区域的人找完后满足5人或者6人，说明人找齐了,叫新车
                        carorder.append(tmpcarorder)
                        break
                    else:
                        # 当前区域的人数不够先寻找距离本区域边界只有100m的点
                        neighborareaidx = getneighbor.theneighborarea(arealoclist, allgetonthecaridx, currentarea,
                                                                      restorderLoc, areaneighbor[currentarea])
                        if neighborareaidx is not None:
                            for neighidx in neighborareaidx:
                                if numPassenger + restSeatNoVec[neighidx] <= CARSEATS:
                                    allgetonthecaridx.append(neighidx)
                                    tmpcarorder.append(neighidx)
                                    numPassenger += restSeatNoVec[neighidx]
                                    keypointDistVec[neighidx] = 0
                                    if numPassenger == CARSEATS:
                                        break  # 结束循环
            if numPassenger == fivecarset or numPassenger == CARSEATS:
                # 当前区域和临近区域都找完后发现人满了那么就结束这次找人，如果没满就继续下一个区域寻找
                carorder.append(tmpcarorder)
                break
            # 当前区域已经没有人了，或是当前区域的人已经被找完，当前点为当前区域的最后一个点
            # 2、寻找1500m范围的人，1可以找1和2,2只能找2
            allneighborhoodIdxVec = auxfn.getNeighborhoodIdx(orderVec, orderVec[firstPassengerIdx, :], SEARCHRADIUS, firstPassengerIdx, restsideVec)
            neighborhoodIdxVec = [x for x in allneighborhoodIdxVec if x not in allgetonthecaridx]
            if len(neighborhoodIdxVec) > 0:
                for neighboridx in neighborhoodIdxVec:
                    if numPassenger + restSeatNoVec[neighboridx] <= CARSEATS:
                        numPassenger += restSeatNoVec[neighboridx]
                        allgetonthecaridx.append(neighboridx)
                        tmpcarorder.append(neighboridx)
                        firstPassengerIdx = neighboridx
                        keypointDistVec[firstPassengerIdx] = 0
                        break
            if firstPassengerIdx in neighborhoodIdxVec:
                # 如果增加了人那么就判断是否坐满了
                if numPassenger == CARSEATS or numPassenger == fivecarset:
                    if numPassenger == fivecarset and restorderNum - len(allgetonthecaridx) == 1:
                        lastpersonindex = np.argmax(keypointDistVec)
                        if numPassenger + restSeatNoVec[lastpersonindex] == CARSEATS:
                            carlastpersonloc = restorderLoc[firstPassengerIdx]
                            lastpersonloc = restorderLoc[lastpersonindex]
                            lastdistance = auxfn.calcDist(carlastpersonloc, lastpersonloc)
                            if lastdistance <= SEARCHRADIUS:
                                allgetonthecaridx.append(lastpersonindex)
                                tmpcarorder.append(lastpersonindex)
                    carorder.append(tmpcarorder)
                    break  # 打破循环找一辆新车
                # 如果没有增加人那么就寻找一个顺路的人
            else:
                # 4、周围没有点那就寻找顺路的点，顺路的定义为，到机场的距离小于当前点且与机场之间的夹角小于15
                ix = np.where(np.in1d(np.arange(restorderNum), allgetonthecaridx, invert=True))
                if len(ix[0]) == 0:  # 最后一个人直接上车
                    carorder.append(tmpcarorder)
                    break
                else:
                    # 当前点side为1可以选择所有的点找周围的点，当前点为2就只能找2
                    currentside = restsideVec[firstPassengerIdx]
                    tmpnextPassengerIdx = auxfn.getSortedPointIdx(orderVec[ix[0], :],
                                                                      orderVec[firstPassengerIdx, :],
                                                                      restsideVec[ix[0]], currentside)
                    ontheway = [ix[0][y] for y in tmpnextPassengerIdx]
                    # ontheway = dis.checkLongdiscondition(tmpcarorder, restorderLoc, tmpPassengerIdx)
                    # 周围没有人且顺路的人也没有那么就直接上车了
                if len(ontheway) == 0:
                    carorder.append(tmpcarorder)
                    break
                else:
                    # 车上没有6个人，周围有人，但是周围上车后车上最小的人数都大于6就结束循环叫新车或是最小的时间都大于限制
                    # 时间限制暂时没有写（后面加上速度后补上）
                    neighborGetOnCar = [restSeatNoVec[element] for element in ontheway]
                    carseatsWithNeighbor = np.array(neighborGetOnCar) + numPassenger
                    # 如果没有满足条件上车的人那么就直接上车
                    if carseatsWithNeighbor.min() > CARSEATS:
                        carorder.append(tmpcarorder)
                        break
                    # 一定会拿到一个人
                    for npidx in ontheway:
                        if numPassenger + restSeatNoVec[npidx] <= CARSEATS:
                            numPassenger += restSeatNoVec[npidx]
                            allgetonthecaridx.append(npidx)
                            tmpcarorder.append(npidx)
                            firstPassengerIdx = npidx
                            keypointDistVec[firstPassengerIdx] = 0
                            break
                    # 如果增加了人那么判断是否够人，如果没有增加人那么说明周围已经没有人了
                    if numPassenger == CARSEATS or numPassenger == fivecarset:
                        if numPassenger == fivecarset and restorderNum - len(allgetonthecaridx) == 1:
                            lastpersonindex = np.argmax(keypointDistVec)
                            if numPassenger + restSeatNoVec[lastpersonindex] == CARSEATS:
                                carlastpersonloc = restorderLoc[firstPassengerIdx]
                                lastpersonloc = restorderLoc[lastpersonindex]
                                lastdistance = auxfn.calcDist(carlastpersonloc, lastpersonloc)
                                if lastdistance <= SEARCHRADIUS:
                                    allgetonthecaridx.append(lastpersonindex)
                                    tmpcarorder.append(lastpersonindex)
                        carorder.append(tmpcarorder)
                        break  # 打破循环找一辆新车
    carOrderList = dis.getThePassengerOrderForEachCar(carorder, restorderNo)
    return carOrderList









