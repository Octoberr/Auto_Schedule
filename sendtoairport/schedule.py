# coding:utf-8

"""
Donghui Chen, Wangmeng Song
May 15, 2017
修改
Wangmeng Song
June 17,2017
June 29, 2017
June 30,2017
改BUG指派司机一辆车超过6个人的情况
July 12,2017
"""
import numpy as np
import copy

import knapsack
import auxfn
import mapAPI

AMAPAIRPORTCOORDINATE = [30.574590, 103.955020]
MAXSEATNUM5 = 5
MAXSEATNUM6 = 6
NORTH = 30.604043
CHENGDULAT = 30.6
LONGDISlIMT = 4500
SEARCHLOOP = 500
# 经度分割(百度)
longDistinguish = 104.074086


class DIST:

    def getTheSpecifyAndNormal(self,specifyDriverDic, normalPassengerDic, resdict):
        for element in resdict:
            if 'driver' not in element.keys() or element['driver'] is None or element['driver'] is u"":
                normalPassengerDic.append(element)
            else:
                specifyDriverDic.append(element)

    def leftandrightgetonthecar(self, getonthecar, northOrderID, northOrderLoc, ):
        leftgetonthecar = []
        rightgetonthtecar = []
        for i in range(len(northOrderLoc)):
            if northOrderLoc[i][1] <= longDistinguish:
                leftgetonthecar += northOrderID[i]
            else:
                rightgetonthtecar += northOrderID[i]
        if len(leftgetonthecar) is not 0:
            getonthecar.append(leftgetonthecar)
        if len(rightgetonthtecar) is not 0:
            getonthecar.append(rightgetonthtecar)

    # 获取指定上车司机的乘客订单
    def getTheSpecifyDriverOrder(self, northOrderID, northOrderLoc, northOrderSeatnum, specifyDriverDic):
        specifyOrderLoc = []
        specifyOrderID = []
        specifyOrderSeatNo = []
        specifyDriver = []
        getSpecifyLoc = []
        getSpecifyID = []
        getSpecifySN = []
        carSpecifyList = []
        for element in specifyDriverDic:
            tmp = []
            bdLat = element['bdlat']
            bdLng = element['bdlng']
            loc = auxfn.BD2AMap(bdLat, bdLng)
            gglat = round(loc.lat, 6)
            gglng = round(loc.lng, 6)
            poid = element['BID']
            seatnum = element['seatnum']
            tmp.append(gglat)
            tmp.append(gglng)
            driverID = element['driver']
            specifyOrderLoc.append(tuple(tmp))  # [(),(),()]
            specifyOrderID.append(poid)         # [a,b,c]
            specifyOrderSeatNo.append(seatnum)      # [1,2,3]
            specifyDriver.append(driverID)         # [101,201,301]
        dupSpecifyDriver = list(set(specifyDriver))  # 获得唯一的司机标识
        for element1 in dupSpecifyDriver:
            repeat = auxfn.getAllIndices(element1, specifyDriver)
            tmploc = []
            tmpid = []
            tmpSN = []
            for element2 in repeat:
                tmploc.append(specifyOrderLoc[element2])
                tmpid.append(specifyOrderID[element2])
                tmpSN.append(specifyOrderSeatNo[element2])
            getSpecifyLoc.append(tmploc)   # [[(),(),()],[(),()]]
            getSpecifyID.append(tmpid)      # [[q,b,c],[d,f]]
            getSpecifySN.append(tmpSN)      # [[1,1,1],[2,2]]
        for i in range(len(getSpecifySN)):
            if sum(getSpecifySN[i]) <= MAXSEATNUM6:
                carSpecifyList.append(getSpecifyID[i])
            else:
                tmpspecialID = copy.copy(getSpecifyID[i])
                tmpspecialseats = copy.copy(getSpecifySN[i])
                allseatnums = sum(tmpspecialseats)
                needcar = allseatnums/MAXSEATNUM6
                leftpas = allseatnums % MAXSEATNUM6
                if leftpas is 0:  # 刚好能坐整数辆车
                    for n in range(needcar):
                        sixpassengeer = knapsack.zeroOneKnapsack(tmpspecialseats, MAXSEATNUM6)
                        storeindex = [j for j, x in enumerate(sixpassengeer[1]) if x is 1]
                        tmpstoreID = []
                        for idx in storeindex:
                            tmpstoreID.append(tmpspecialID[idx])
                        carSpecifyList.append(tmpstoreID)
                        for delidx in reversed(storeindex):
                            del (tmpspecialID[delidx])
                            del (tmpspecialseats[delidx])
                else:  # 人数刚好不能坐辆车
                    for m in range(needcar):
                        average = allseatnums/(needcar+1)
                        averagepass = knapsack.zeroOneKnapsack(tmpspecialseats, average)
                        mstoreindex = [k for k, l in enumerate(averagepass[1]) if l is 1]
                        mtmpstoreID = []
                        for idx in mstoreindex:
                            mtmpstoreID.append(tmpspecialID[idx])
                        carSpecifyList.append(mtmpstoreID)
                        for delidx in reversed(mstoreindex):
                            del (tmpspecialID[delidx])
                            del (tmpspecialseats[delidx])
                    carSpecifyList.append(tmpspecialID)
                    # for i in xrange(len(getSpecifyLoc)):
        #     if sum(getSpecifySN[i]) is 5 or sum(getSpecifySN[i]) is 6:
        #         carSpecifyList.append(getSpecifyID[i])
        #     else:
        #         cartmp = getSpecifyID[i]
        #         passenger = sum(getSpecifySN[i])
        #         tmpdelarrange = []
        #         for j in xrange(len(getSpecifyLoc[i])):
        #             tdNorthOrderVec = self.getOrderLocVec(northOrderLoc)
        #             neighborhoodIdxVec1 = auxfn.getNeighborhoodIdx(tdNorthOrderVec, getSpecifyLoc[i][j], SEARCHLOOP)
        #             neighborhoodIdxVec = [x for x in neighborhoodIdxVec1 if x not in tmpdelarrange]
        #             if len(neighborhoodIdxVec) >= 1:
        #                 for neighbor in neighborhoodIdxVec:
        #                     if passenger+sum(northOrderSeatnum[neighbor]) <= MAXSEATNUM6:
        #                         cartmp += northOrderID[neighbor]
        #                         tmpdelarrange.append(neighbor)
        #                         passenger += sum(northOrderSeatnum[neighbor])
        #                     else:
        #                         continue
        #             if (passenger is 5) or (passenger is 6):  # 当满足条件直接上车
        #                 carSpecifyList.append(cartmp)
        #                 tmpdelarrange.sort()
        #                 for element3 in reversed(tmpdelarrange):
        #                     del(northOrderID[element3])
        #                     del(northOrderLoc[element3])
        #                     del(northOrderSeatnum[element3])
        #                 break
        #             elif j is len(getSpecifyLoc[i])-1:    # 当最后一个人都没有找到同伴就直接上车
        #                 carSpecifyList.append(cartmp)
        #                 tmpdelarrange.sort()
        #                 for element3 in reversed(tmpdelarrange):
        #                     del (northOrderID[element3])
        #                     del (northOrderLoc[element3])
        #                     del (northOrderSeatnum[element3])
        return carSpecifyList

    # 初步处理数据，传入json字符串resdict,订单人数=5/6的存入getonthecar,getonthecarloc,getonthecarseatnum
    def getAllRepeatData(self, repeatpoid, repeatloc, repeatseatnum, getonthecar, getonthecarloc, getonthecarseatnum, resdict):
        for element in resdict:
            tmp = []
            bdLat = element['bdlat']
            bdLng = element['bdlng']
            loc = auxfn.BD2AMap(bdLat, bdLng)
            gglat = round(loc.lat, 6)
            gglng = round(loc.lng, 6)
            poid = element['BID']
            seatnum = element['seatnum']
            tmp.append(gglat)
            tmp.append(gglng)
            if seatnum is 6 or seatnum is 5:
                getonthecar.append([poid])
                getonthecarloc.append(tuple(tmp))
                getonthecarseatnum.append([seatnum])
            else:
                repeatpoid.append(poid)
                repeatseatnum.append(seatnum)
                repeatloc.append(tuple(tmp))

    # 第二次处理数据，将同一地点的订单集中在一起，duplicateLoc=[[(lat,lng),(lat,lng)]],duplicateorderid=[[ordea,orderb],[orderc]]
    def getDuplicateData(self, repeatOrderID, repeatloc, repeatSeatnum, duplicateOrderid, duplicateSeatNum):
        duplicateLoc = list(set(repeatloc))
        for element in duplicateLoc:
            repeat = auxfn.getAllIndices(element, repeatloc)
            orderidtmp = []
            seatnumtmp = []
            for element1 in repeat:
                orderidtmp.append(repeatOrderID[element1])
                seatnumtmp.append(repeatSeatnum[element1])
            duplicateOrderid.append(orderidtmp)
            duplicateSeatNum.append(seatnumtmp)
        return duplicateLoc

    # 第三次处理数据排除一个地点中=5/6的情况，如果这个地点人数大于6，那么将订单人数相加=5/6存入getonthecar，剩下的订单存入RMMTSID，RMMTSLoc
    def removeMoreThanSixPassenger(self, ID, Loc, Seatnum, RMMTSID, RMMTSLoc, RMMTSseatnum, getontcar, getonthecaloc, getonthecarseatnum):
        for i in range(len(Seatnum)):
            if sum(Seatnum[i]) is MAXSEATNUM6 or sum(Seatnum[i]) is MAXSEATNUM5:
                getontcar.append(ID[i])
                getonthecaloc.append(Loc[i])
                getonthecarseatnum.append(Seatnum[i])
            elif sum(Seatnum[i]) > MAXSEATNUM6:
                tmpSeatnum = copy.copy(Seatnum[i])
                tmpID = copy.copy(ID[i])
                knapsack6 = knapsack.zeroOneKnapsack(tmpSeatnum, MAXSEATNUM6)
                knapsack5 = knapsack.zeroOneKnapsack(tmpSeatnum, MAXSEATNUM5)
                while knapsack6[0] is MAXSEATNUM6 or knapsack5[0] is MAXSEATNUM5:
                    if knapsack6[0] is 6:
                        knapsackvalue = knapsack6[1]
                    else:
                        knapsackvalue = knapsack5[1]
                    tmpalreadygetonthcarid = []
                    storeindex = [j for j, x in enumerate(knapsackvalue) if x is 1]      # 列表推导式
                    for element1 in storeindex:
                        tmpalreadygetonthcarid.append(tmpID[element1])
                    getontcar.append(tmpalreadygetonthcarid)
                    getonthecaloc.append(Loc[i])
                    getonthecarseatnum.append(Seatnum[i])
                    for element2 in reversed(storeindex):
                        del (tmpSeatnum[element2])
                        del (tmpID[element2])
                    if len(tmpSeatnum) > 1:
                        knapsack6 = knapsack.zeroOneKnapsack(tmpSeatnum, MAXSEATNUM6)
                        knapsack5 = knapsack.zeroOneKnapsack(tmpSeatnum, MAXSEATNUM5)
                    elif len(tmpSeatnum) is 1:
                        RMMTSID.append(tmpID)
                        RMMTSLoc.append(Loc[i])
                        RMMTSseatnum.append(tmpSeatnum)
                        break
                    else:
                        break
                else:
                    if sum(tmpSeatnum) < 6:
                        RMMTSID.append(tmpID)
                        RMMTSLoc.append(Loc[i])
                        RMMTSseatnum.append(tmpSeatnum)
                    else:                                       # 增加同一个地点大于6个人订单情况
                        tmpLoc = list(Loc[i])
                        r = 0
                        for k in xrange(len(tmpID)):
                            tmpLoc[0] += r
                            tmpLoc[1] += r
                            RMMTSID.append([tmpID[k]])
                            RMMTSLoc.append(tuple(tmpLoc))
                            RMMTSseatnum.append([tmpSeatnum[k]])
                            r += 0.00001
            else:
                RMMTSID.append(ID[i])
                RMMTSLoc.append(Loc[i])
                RMMTSseatnum.append(Seatnum[i])

    # 如果已经上车的且订单中人数=5，那么寻找它1000米范围内的一个人，如果有就上车且在RMMSID、RMMSLoc、RMMTSseatnum中删除订单信息，如果没有就什么不做
    def getTheFivePersonAroundOnlyOne(self, getonthecar, getonthecarloc, getonthecarseatnum, RMMTSID, RMMTSLoc, RMMTSseatnum):
        tmpRMMTSLoc = copy.copy(RMMTSLoc)
        tmpRMMTSLocVec = self.getOrderLocVec(tmpRMMTSLoc)
        frelement = []
        for i in range(len(getonthecarseatnum)):
            if sum(getonthecarseatnum[i]) is MAXSEATNUM5:   # 修改==为is提高效率
                arounddistvec = auxfn.calcDistVec(getonthecarloc[i], tmpRMMTSLocVec)
                tmpix = np.where(arounddistvec < 1001)
                if len(tmpix[0]) is not 0:
                    ix = [x for x in tmpix[0] if x not in frelement]
                    if len(ix) is not 0:
                        for element in ix:
                            if len(RMMTSseatnum[element]) is 1 and RMMTSseatnum[element][0] is 1:
                                frelement.append(element)
                                getonthecar[i].append(RMMTSID[element][0])
                            else:
                                continue
                    else:
                        continue
                else:
                    continue
            else:
                continue
        if len(frelement) is not 0:
            frelement.sort()
            for element2 in reversed(frelement):
                RMMTSID.pop(element2)
                RMMTSLoc.pop(element2)
                RMMTSseatnum.pop(element2)

    # 区分南北订单
    def distinguish(self, getonthecar, getonthecarloc, getonthecarseatnum, RMMTSID, RMMTSLoc, RMMTSseatnum, northOrderID, northOrderLoc, northOrderSeatnum):
        for i in xrange(len(RMMTSLoc)):
            if RMMTSLoc[i][0] > NORTH:
                northOrderID.append(RMMTSID[i])
                northOrderLoc.append(RMMTSLoc[i])
                northOrderSeatnum.append(RMMTSseatnum[i])
            else:
                getonthecar.append(RMMTSID[i])
                getonthecarloc.append(RMMTSLoc[i])
                getonthecarseatnum.append(RMMTSseatnum[i])

    # 检查乘客在车上呆的时间是否满足小于最大时间
    def checkTimeLimitCondition(self, maxTimeLimit, currentPoint, nextPoint, airport, currentScheduleVec, currentPasIdx, nexPoinIdx):
        GTI = mapAPI.AMapAPI()
        deltaT = GTI.getTimeDistVec(nextPoint, currentPoint, 1)
        nextPoint2airportTime = GTI.getTimeDistVec(airport, nextPoint, 1)
        if np.sum(currentScheduleVec) + deltaT + nextPoint2airportTime - currentScheduleVec[0] <= maxTimeLimit:
            currentScheduleVec.append(deltaT[0])
            currentPasIdx.append(nexPoinIdx)
            currentScheduleVec[0] = nextPoint2airportTime[0]
            return True
        else:
            return False

    def checkLongdiscondition(self, currenPasIdxVec, allOrderLoc, nexpasIdx):
        nextpassenger = []
        for i in xrange(len(nexpasIdx)):
            longDist = 0
            if len(currenPasIdxVec) is 1:
                longDist += auxfn.calcDist((CHENGDULAT, allOrderLoc[currenPasIdxVec[0]][1]), (CHENGDULAT, allOrderLoc[nexpasIdx[i]][1]))
            else:
                for j in xrange(len(currenPasIdxVec)):
                    longDist += auxfn.calcDist((CHENGDULAT, allOrderLoc[currenPasIdxVec[j]][1]), ((CHENGDULAT, allOrderLoc[currenPasIdxVec[j+1]][1])))
                    if j+1 is len(currenPasIdxVec)-1:
                        longDist += auxfn.calcDist((CHENGDULAT, allOrderLoc[currenPasIdxVec[j+1]][1]), (CHENGDULAT, allOrderLoc[nexpasIdx[i]][1]))
                        break
            if longDist <= LONGDISlIMT:
                nextpassenger.append(nexpasIdx[i])
        return nextpassenger

    # 将orderLocList=[(lat1,lng1),(lat2,lng2)]，转换为2-Darray orderLocVec = [[lat1 lng],[lat2 lng2]]
    def getOrderLocVec(self, orderLocList):
        orderLocVec = np.zeros([len(orderLocList), 2], dtype=float)
        for i in range(len(orderLocList)):
            orderLocVec[i][0] = orderLocList[i][0]
            orderLocVec[i][1] = orderLocList[i][1]
        return orderLocVec

    # 将一个地点的人数orderSeatNumList = [[2],[1,1,1],[2,2]]求和转化为1维数组，orderNum = [2 3 4]
    def getOrderNumVec(self, orderSeatNumList):
        orderNum = np.zeros([len(orderSeatNumList)], dtype='uint')
        for i in range(len(orderSeatNumList)):
            orderNum[i] = sum(orderSeatNumList[i])
        return orderNum

    # 获取一辆车的乘客数据格式为[[2,4,1],[5,6,7]]
    def getCarPassengerList(self, timeList, passengerList):
        numList = []
        for element in timeList:
            numList.append(len(element))
        newNumList = []
        for i in xrange(len(numList) + 1):
            newNumList.append(sum(numList[0:i]))
        carList = []
        for j in xrange(1, len(newNumList)):
            tem = []
            for k in xrange(newNumList[j - 1], newNumList[j]):
                tem.append(passengerList[k])
            carList.append(tem)
        return carList

    # 将一辆车的地点替换为订单[[[A,B],[C],[D]],[[E],[F],[G]]]
    def getThePassengerOrderForEachCar(self, carList, orderID):
        carOrderList = []
        for i in xrange(len(carList)):
            car = []
            for element in carList[i]:
                car += orderID[element]
            carOrderList.append(car)
        return carOrderList

    # 将时间添加到订单单信息中[[[A,1800],[B,1800],[C,500],[D,100]],[[E,2000],[F,1000],[G,500]]]
    def getOrderAndTimeInfos(self, carOrderList, OrderTime):
        ret = []
        for m in xrange(len(OrderTime)):
            ret.append([])
            for n in xrange(len(OrderTime[m])):
                sum0 = sum(OrderTime[m])
                sum0 -= sum(OrderTime[m][1:n + 1])
                val = carOrderList[m][n]
                for element in val:
                    tmp = []
                    tmp.append(element)
                    tmp.append(sum0)
                    ret[m].append(tmp)
        return ret


# 获得已经上车的乘客的时间距离getonthecarloc=[(lat1,lng1),(lat2,lng2)],getonthecarorderid=[[A,B,C],[D,E]]
    def gethasgotonthecartimedistance(self, getonthecarloc, getonthecarorderid):
        GTI = mapAPI.AMapAPI()
        if len(getonthecarloc) is not 1:
            orderVec = self.getOrderLocVec(getonthecarloc)
            orderNum = len(orderVec)
        else:
            orderVec = np.array([getonthecarloc[0][0], getonthecarloc[0][1]])
            orderNum = len(getonthecarloc)
        timedistancevec = GTI.getTimeDistVec(AMAPAIRPORTCOORDINATE, orderVec,orderNum)
        hasgetonthecarorderandtime = []    # [[[a,878],[b,788],[c,898]],[[d,658],[e,345]]]
        for i in range(orderNum):
            car = []
            for j in range(len(getonthecarorderid[i])):
                tmp = []
                tmp.append(getonthecarorderid[i][j])
                tmp.append(timedistancevec[i])
                car.append(tmp)
            hasgetonthecarorderandtime.append(car)
        return hasgetonthecarorderandtime

# 使用tsp算法进行排序（f**k this tsp）
    def sortPassenger(self, carList, northOrderLoc):
        sortcarList =[]
        for element in carList:
            onecarpassenger = []
            for element2 in element:
                onecarpassenger.append(northOrderLoc[element2])
            t = tsp(onecarpassenger)
            t.solve()
            sortcarList.append(t.result)
        return sortcarList



