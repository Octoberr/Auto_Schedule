# coding:utf-8

"""
creat by swm
重写排班的处理方法
20170915
"""
# 外部引用
import numpy as np
from compiler.ast import flatten
# 内部引用
import schedule
from recomTimeOnTheBus import eastandwestside
from recomTimeOnTheBus import getneighbor


def startschedul(resdict):
    dis = schedule.DIST()   # 实例化DIST类
    area = eastandwestside.SIDE()  # 实例化区分区域的类
    normalPassengerDic = []  # 存储普通乘客的订单，局部变量用于下一次使用
    # 分离普通乘客的订单和指定司机的订单
    specifyDriverDic = dis.getTheSpecifyAndNormal(normalPassengerDic, resdict)
    # 处理指定司机的订单
    if len(specifyDriverDic) > 0:
        specifyDriverOrder = dis.getTheSpecifyDriverOrder(specifyDriverDic)
    else:
        specifyDriverOrder = []
    # return specifyDriverOrder
    advanceGetOnTheCar = []  # 存储所有预先处理后需要提前上车的订单
    # 处理所有的订单，将关键数据订单号和seatnum转化为list,repeatdicInfo，将一个订单5/6的提前上车
    repeatdicInfo = dis.getAllRepeatData(advanceGetOnTheCar, normalPassengerDic)
    # 获取同一个地点的订单，并且合并以一个点为中心的100m范围的订单
    duplicateInfo = dis.getDuplicateData(repeatdicInfo)
    # 过滤一个地点5/6的订单，将一个地点5/6的订单提前上车
    rmtspID = []
    rmtspLoc = []
    rmtspSeat = []
    dis.removeMoreThanSixPassenger(rmtspID, rmtspLoc, rmtspSeat, duplicateInfo, advanceGetOnTheCar)
    # 对每个订单进行所在的去与标记出来，用来判断是会否在排班拼车范围或者是
    rmarealoclist = []  # 每个idx对应的区域范围
    getonthecarlist = []
    for loc in range(len(rmtspLoc)):
        areanum = getneighbor.findtheareanumber(rmtspLoc[loc][0], rmtspLoc[loc][1])
        if areanum is not None:
            rmarealoclist.append(areanum)
        else:
            # 超出范围上车
            getonthecarlist.append(loc)
    # 判断一下是否有超出范围提前上车了的订单
    if len(getonthecarlist) > 0:
        for el in getonthecarlist:
            advanceGetOnTheCar.append(rmtspID[el])
        for delel in reversed(getonthecarlist):
            del (rmtspID[delel])
            del (rmtspLoc[delel])
            del (rmtspSeat[delel])
    # 进入调用schedule的订单数
    orderNum = len(rmtspLoc)     # 进入排班算法的总地点数
    seatNumVec = dis.getOrderNumVec(rmtspSeat)  # 二维的乘客人数转换为与地点对应的一维数组 array[3,1]
    sidevec = area.ateast(orderNum, rmarealoclist)   # 地区东边和西边的代码，地图东为1，西为2,array
    eastareaVec = np.where(sidevec <= 1)[0]  # 东边地区的index集合，一维array
    westareaVec = np.where(sidevec >= 2)[0]  # 西边地区的index集合，一维array
    # 如果东边和西边的人数同时小于或等于6就分别上车
    if sum(seatNumVec[eastareaVec]) <= 6 and sum(seatNumVec[westareaVec]) <= 6:
        eastcar = [rmtspID[e] for e in eastareaVec]
        if len(eastcar) > 0:
            eastloc = [rmtspLoc[lc] for lc in eastareaVec]
            eastcarpool = [ewd for (elc, ewd) in sorted(zip([elat[0] for elat in eastloc], eastcar), reverse=True)]
            advanceGetOnTheCar.append(flatten(eastcarpool))
        westcar = [rmtspID[w] for w in westareaVec]
        if len(westcar) > 0:
            westloc = [rmtspLoc[wl] for wl in westareaVec]
            westcarpool = [wd for (lc, wd) in sorted(zip([lat[0] for lat in westloc], westcar), reverse=True)]
            advanceGetOnTheCar.append(flatten(westcarpool))
        AllCarOrder = advanceGetOnTheCar + specifyDriverOrder
        return AllCarOrder
    # 如果东边小于等于6，西边大于6,东边上车
    elif sum(seatNumVec[eastareaVec]) <= 6 and sum(seatNumVec[westareaVec]) > 6:
        eastcar = [rmtspID[e] for e in eastareaVec]
        if len(eastcar) > 0:
            eastloc = [rmtspLoc[f] for f in eastareaVec]
            carpool = [wd for (lc, wd) in sorted(zip([lat[0] for lat in eastloc], eastcar), reverse=True)]
            advanceGetOnTheCar.append(flatten(carpool))
            for delindex in reversed(eastareaVec):
                del (rmtspID[delindex])
                del (rmtspLoc[delindex])
                del (rmtspSeat[delindex])
        restorderNo = []  # [[A,,B,C],[D,E,F]]
        restorderLoc = []  # [(lat1,lng1),(lat2,lng2)]
        restorderSeatNo = []  # [[1,2,3],[2,3]]
        newwestareaVec = np.arange(len(rmtspLoc))
        dis.westschedule(rmtspID, rmtspLoc, rmtspSeat, newwestareaVec, restorderNo, restorderLoc, restorderSeatNo, advanceGetOnTheCar)
        if sum(flatten(restorderSeatNo)) <= 6:
            if len(restorderSeatNo) > 0:
                carsorted = [wd for (lc, wd) in sorted(zip([lat[0] for lat in restorderLoc], restorderNo), reverse=True)]
                advanceGetOnTheCar.append(flatten(carsorted))
            AllCarOrder = advanceGetOnTheCar + specifyDriverOrder
            return AllCarOrder
        else:
            import schedulelogic
            carOrderList = schedulelogic.slogic(restorderNo, restorderLoc, restorderSeatNo)
            quecarorder = dis.quescheduel(carOrderList, restorderNo, restorderLoc)
            AllCarOrder = quecarorder + advanceGetOnTheCar + specifyDriverOrder
            return AllCarOrder
    elif sum(seatNumVec[eastareaVec]) > 6 and sum(seatNumVec[westareaVec]) <= 6:
        westcar = [rmtspID[w] for w in westareaVec]
        if len(westcar) > 0:
            westloc = [rmtspLoc[g] for g in westareaVec]
            carpool = [wd for (lc, wd) in sorted(zip([lat[0] for lat in westloc], westcar), reverse=True)]
            advanceGetOnTheCar.append(flatten(carpool))
            for delindex in reversed(westareaVec):
                del(rmtspID[delindex])
                del(rmtspLoc[delindex])
                del(rmtspSeat[delindex])
        import schedulelogic
        carOrderList = schedulelogic.slogic(rmtspID, rmtspLoc, rmtspSeat)
        quecarorder = dis.quescheduel(carOrderList, rmtspID, rmtspLoc)
        AllCarOrder = quecarorder + advanceGetOnTheCar + specifyDriverOrder
        return AllCarOrder
    else:
        # 对订单在西边2环到2.5环的情况进行排班
        restorderNo = []   # [[A,,B,C],[D,E,F]]
        restorderLoc = []   # [(lat1,lng1),(lat2,lng2)]
        restorderSeatNo = []    # [[1,2,3],[2,3]]
        # 西边2环到2.5环的优先派单
        dis.westschedule(rmtspID, rmtspLoc, rmtspSeat, westareaVec, restorderNo, restorderLoc, restorderSeatNo,
                         advanceGetOnTheCar)
        import schedulelogic
        carOrderList = schedulelogic.slogic(restorderNo, restorderLoc, restorderSeatNo)
        quecarorder = dis.quescheduel(carOrderList, restorderNo, restorderLoc)
        AllCarOrder = quecarorder + advanceGetOnTheCar + specifyDriverOrder
        return AllCarOrder

