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
July 21,2017
August 16, 2017 修改接人顺序
"""
import numpy as np
import copy
from sklearn.neighbors import NearestNeighbors
from compiler.ast import flatten

import knapsack
import auxfn
import mapAPI
from recomTimeOnTheBus import eastandwestside

AMAPAIRPORTCOORDINATE = [30.574590, 103.955020]
MAXSEATNUM5 = 5
MAXSEATNUM6 = 6
NORTH = 30.604043
CHENGDULAT = 30.6
LONGDISlIMT = 4500
SEARCHLOOP = 500
# 经度分割(百度)
longDistinguish = 104.074086
# 西北边3000米
westradius = 3000
highlat = 30.674533


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
            else:  # 指定的某个司机的人数大于6个人的情况，使用背包装金算法分人
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

    # 如果已经上车的且订单中人数=5，那么寻找它500米范围内的一个人，如果有就上车且在RMMSID、RMMSLoc、RMMTSseatnum中删除订单信息，如果没有就什么不做
    def getTheFivePersonAroundOnlyOne(self, getonthecar, getonthecarloc, getonthecarseatnum, RMMTSID, RMMTSLoc, RMMTSseatnum):
        tmpRMMTSLoc = copy.copy(RMMTSLoc)
        tmpRMMTSLocVec = self.getOrderLocVec(tmpRMMTSLoc)
        frelement = []
        for i in range(len(getonthecarseatnum)):
            if sum(getonthecarseatnum[i]) is MAXSEATNUM5:   # 修改==为is提高效率
                arounddistvec = auxfn.calcDistVec(getonthecarloc[i], tmpRMMTSLocVec)
                tmpix = np.where(arounddistvec < 501)  # 寻找500米的范围
                if len(tmpix[0]) is not 0:
                    ix = [x for x in tmpix[0] if x not in frelement]
                    if len(ix) is not 0:
                        for element in ix:
                            if len(RMMTSseatnum[element]) is 1 and RMMTSseatnum[element][0] is 1:
                                frelement.append(element)
                                getonthecar[i].append(RMMTSID[element][0])
                                break
                            else:
                                continue
                    else:
                        continue
                else:
                    continue
            else:
                continue
        if len(frelement) is not 0:
            for element2 in frelement:
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
                    if j+1 == len(currenPasIdxVec)-1:
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
        orderNum = np.zeros([len(orderSeatNumList)], dtype='int')
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
        timedistancevec = GTI.getTimeDistVec(AMAPAIRPORTCOORDINATE, orderVec, orderNum)
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

    # 处理西边的订单得到剩下的进入排班的订单
    def westschedule(self, northOrderID, northOrderLoc, northOrderSeatnum, westareaVec, restorderNo, restorderLoc, restorderSeatNo, getonthcar):
        sd = eastandwestside.SIDE()
        westorderID = []    # [[A,,B,C],[D,E,F]]
        westorderLoc = []   # [(lat1,lng1),(lat2,lng2)]
        westorderSeatNo = []     # [[1,2,3],[2,3]]
        for index in westareaVec:
            westorderID.append(northOrderID[index])
            westorderLoc.append(northOrderLoc[index])
            westorderSeatNo.append(northOrderSeatnum[index])
        # 将总订单中西边的订单删除
        for delinx in reversed(westareaVec):
            del (northOrderID[delinx])
            del (northOrderLoc[delinx])
            del (northOrderSeatnum[delinx])
        # 判断西边的订单人数，如果小于6就直接上车，return，restdingdan
        # 寻找2.5环和2环之间的订单，1表示在2环到2.5环之间
        westoutsideNo = sd.atwest2out(westorderLoc, len(westorderLoc))
        outsideIndex = np.where(westoutsideNo <= 1)[0]  # 在2环和2.5环的index
        if len(outsideIndex) is 0:
            restorderNo += northOrderID + westorderID
            restorderLoc += northOrderLoc + westorderLoc
            restorderSeatNo += northOrderSeatnum + westorderSeatNo
            return
        outsideNumVec = self.getOrderNumVec(westorderSeatNo)  # 二维的乘客人数转换为与地点对应的一维数组 array[3,1]
        # 二环到2.5环的人刚好为5或者6
        if sum(outsideNumVec[outsideIndex]) == 5 or sum(outsideNumVec[outsideIndex]) == 6:
            callcar = []
            callloc = []
            for out in outsideIndex:
                callcar.append(westorderID[out])
                callloc.append(westorderLoc[out])
            # 两个列表的排序，car的顺序是有loc中lat的顺序决定的
            acar = [wd for (lc, wd) in sorted(zip([lat[0] for lat in callloc], callcar), reverse=True)]
            getonthcar.append(flatten(acar))
            for delout in reversed(outsideIndex):
                del (westorderID[delout])
                del (westorderLoc[delout])
                del (westorderSeatNo[delout])
            restorderNo += northOrderID + westorderID
            restorderLoc += northOrderLoc + westorderLoc
            restorderSeatNo += northOrderSeatnum + westorderSeatNo
            return
        # 2环到2.5环的人为3或4，寻找西北的人凑到5个
        elif sum(outsideNumVec[outsideIndex]) <= 4 and sum(outsideNumVec[outsideIndex]) > 2:
            self.coudaofivedingdan(outsideIndex, westorderID, westorderLoc, westorderSeatNo, getonthcar)
            restorderNo += northOrderID + westorderID
            restorderLoc += northOrderLoc + westorderLoc
            restorderSeatNo += northOrderSeatnum + westorderSeatNo
            return
        # 当人数为1或者2的时候不管了直接参与排班
        elif sum(outsideNumVec[outsideIndex]) <= 2:
            restorderNo += northOrderID + westorderID
            restorderLoc += northOrderLoc + westorderLoc
            restorderSeatNo += northOrderSeatnum + westorderSeatNo
            return
        else:
            # 当2环到2.5环的订单人数大于6，预先知道需要几辆车，按纬度顺序上车最后剩下的人参与排班
            outwestID = []  # [[A,,B,C],[D,E,F]]
            outwestLoc = []  # [(lat1,lng1),(lat2,lng2)]
            outwestSeatNo = []  # [[1,1,1], [2,1,1]]
            for outindex in outsideIndex:
                outwestID.append(westorderID[outindex])
                outwestLoc.append(westorderLoc[outindex])
                outwestSeatNo.append(westorderSeatNo[outindex])
            for outdelinx in reversed(outsideIndex):
                del (westorderID[outdelinx])
                del (westorderLoc[outdelinx])
                del (westorderSeatNo[outdelinx])
            # 得到2.5环到2环的订单后按照纬度进行排序
            latQueueIndex = sorted(range(len(outwestLoc)), key=lambda k: outwestLoc[k], cmp=lambda a, b: -1 if a[0] < b[0] else 0)
            locQueue = [outwestLoc[locindex] for locindex in latQueueIndex]
            idQueue = [outwestID[idindex] for idindex in latQueueIndex]
            seatQueue = [outwestSeatNo[seatIndex] for seatIndex in latQueueIndex]
            outsideSeatVec = self.getOrderNumVec(seatQueue)
            while sum(outsideSeatVec) >= MAXSEATNUM5:
                getcarIndex = []
                tmpcar = []
                tmploc = []
                carSeat = 0
                for i in range(len(idQueue)):
                    if carSeat + outsideSeatVec[i] > 6:
                        continue
                    carSeat += outsideSeatVec[i]
                    tmpcar.append(idQueue[i])
                    tmploc.append(locQueue[i])
                    getcarIndex.append(i)
                    if carSeat == MAXSEATNUM5 or carSeat == MAXSEATNUM6:
                        if carSeat == MAXSEATNUM6:
                            carpool = [wd for (lc, wd) in sorted(zip([lat[0] for lat in tmploc], tmpcar), reverse=True)]
                            getonthcar.append(flatten(carpool))
                            for deli in reversed(getcarIndex):
                                del(locQueue[deli])
                                del(idQueue[deli])
                                del(seatQueue[deli])
                            break
                        else:
                            try:
                                if carSeat + outsideSeatVec[i+1] == MAXSEATNUM6:
                                    tmpcar.append(idQueue[i+1])
                                    tmploc.append(locQueue[i+1])
                                    getcarIndex.append(i+1)
                                    carpool = [wd for (lc, wd) in sorted(zip([lat[0] for lat in tmploc], tmpcar), reverse=True)]
                                    getonthcar.append(flatten(carpool))
                                    for deli in reversed(getcarIndex):
                                        del (locQueue[deli])
                                        del (idQueue[deli])
                                        del (seatQueue[deli])
                                    break
                            except:
                                pass
                            carpool = [wd for (lc, wd) in sorted(zip([lat[0] for lat in tmploc], tmpcar), reverse=True)]
                            getonthcar.append(flatten(carpool))
                            for deli in reversed(getcarIndex):
                                del (locQueue[deli])
                                del (idQueue[deli])
                                del (seatQueue[deli])
                            break
                if carSeat == 3 or carSeat == 4:
                    carpool = [wd for (lc, wd) in sorted(zip([lat[0] for lat in tmploc], tmpcar), reverse=True)]
                    getonthcar.append(flatten(carpool))
                    for deli in reversed(getcarIndex):
                        del (locQueue[deli])
                        del (idQueue[deli])
                        del (seatQueue[deli])
                outsideSeatVec = self.getOrderNumVec(seatQueue)
            if sum(outsideSeatVec) <= 4 and sum(outsideSeatVec) > 2:
                self.anotherCouDingdan(idQueue, locQueue, seatQueue, westorderID, westorderLoc, westorderSeatNo, getonthcar)
                restorderNo += northOrderID + westorderID
                restorderLoc += northOrderLoc + westorderLoc
                restorderSeatNo += northOrderSeatnum + westorderSeatNo
            elif sum(outsideSeatVec) <= 2:
                restorderNo += northOrderID + westorderID + idQueue
                restorderLoc += northOrderLoc + westorderLoc + locQueue
                restorderSeatNo += northOrderSeatnum + westorderSeatNo + seatQueue
        return

            # latvalue = [MAXSEATNUM6*n for n in range(1, len(idQueue)+1)]
            # knapsack6 = valueknapsack.zeroOneKnapsack(outsideSeatVec, latvalue, MAXSEATNUM6)
            # knapsack5 = valueknapsack.zeroOneKnapsack(outsideSeatVec, latvalue, MAXSEATNUM5)
            # while knapsack5[0] == MAXSEATNUM5 or knapsack6[0] == MAXSEATNUM6:
            #     if knapsack5[0] == MAXSEATNUM5:
            #         knapsackindex = knapsack5[1]
            #     else:
            #         knapsackindex = knapsack6[1]
            #     tmpgetonthcarid = []
            #     tmpgetonthcarloc = []
            #     for element1 in knapsackindex:
            #         tmpgetonthcarid.append(idQueue[element1])
            #         tmpgetonthcarloc.append(locQueue[element1])
            #     carpool = [wd for (lc, wd) in sorted(zip([lat[0] for lat in tmpgetonthcarloc], tmpgetonthcarid), reverse=True)]
            #     getonthcar.append(flatten(carpool))
            #     # 删除在西部已经上车的订单号
            #     for element2 in reversed(knapsackindex):
            #         del (idQueue[element2])
            #         del (locQueue[element2])
            #         del (seatQueue[element2])
            #     # 重新获取人数vec
            #     outsideSeatVec = self.getOrderNumVec(seatQueue)
            #     latvalue = [MAXSEATNUM6*n for n in range(1, len(idQueue)+1)]
            #     if sum(outsideSeatVec) >= MAXSEATNUM5:
            #         knapsack6 = valueknapsack.zeroOneKnapsack(outsideSeatVec, latvalue, MAXSEATNUM6)
            #         knapsack5 = valueknapsack.zeroOneKnapsack(outsideSeatVec, latvalue, MAXSEATNUM5)
            #     elif sum(outsideSeatVec) <= 4 and sum(outsideSeatVec) > 2:
            #         self.anotherCouDingdan(idQueue, locQueue, seatQueue, westorderID, westorderLoc, westorderSeatNo, getonthcar)
            #         restorderNo += northOrderID + westorderID
            #         restorderLoc += northOrderLoc + westorderLoc
            #         restorderSeatNo += northOrderSeatnum + westorderSeatNo
            #         break
            #     elif sum(outsideSeatVec) <= 2:
            #         restorderNo += northOrderID + westorderID + idQueue
            #         restorderLoc += northOrderLoc + westorderLoc + locQueue
            #         restorderSeatNo += northOrderSeatnum + westorderSeatNo + seatQueue
            #         break
            # return
            # totalPeople = sum(flatten(outwestSeatNo))
            # if totalPeople % MAXSEATNUM5 == 0:
            #     needCars = totalPeople/MAXSEATNUM5
            #     latQueueIndex = sorted(range(len(outwestLoc)), key=lambda k: outwestLoc[k], cmp=lambda a, b: -1 if a[0] > b[0] else 0)
            #     locQueue = [westorderLoc[locindex] for locindex in latQueueIndex]
            #     idQueue = [westorderID[idindex] for idindex in latQueueIndex]
            #     seatQueue = [westorderSeatNo[seatIndex] for seatIndex in latQueueIndex]
            #     for car in range(needCars):
            #         carseat = 0
            #         getindex = []
            #         getcar = []
            #         seatArrayVec = self.getOrderNumVec(seatQueue)
            #         for onCarIndex in range(len(locQueue)):
            #             if carseat + seatArrayVec[onCarIndex] > MAXSEATNUM5:
            #                 continue
            #             carseat += seatArrayVec[onCarIndex]
            #             getcar.append(idQueue[onCarIndex])
            #             getindex.append(onCarIndex)
            #             if carseat == MAXSEATNUM5:
            #                 getonthcar.append(flatten(getcar))
            #                 for delgetindex in reversed(getindex):
            #                     del (locQueue[delgetindex])
            #                     del (idQueue[delgetindex])
            #                     del (seatQueue[delgetindex])
            #                 break
            #     return
            # elif totalPeople % MAXSEATNUM6 == 0:
            #     needCars = totalPeople/MAXSEATNUM6
            #     latQueueIndex = sorted(range(len(outwestLoc)), key=lambda k: outwestLoc[k], cmp=lambda a, b: -1 if a[0] > b[0] else 0)
            #     locQueue = [westorderLoc[locindex] for locindex in latQueueIndex]
            #     idQueue = [westorderID[idindex] for idindex in latQueueIndex]
            #     seatQueue = [westorderSeatNo[seatIndex] for seatIndex in latQueueIndex]
            #     for car in range(needCars):
            #         carseat = 0
            #         getindex = []
            #         getcar = []
            #         seatArrayVec = self.getOrderNumVec(seatQueue)
            #         for onCarIndex in range(len(locQueue)):
            #             if carseat + seatArrayVec[onCarIndex] > MAXSEATNUM6:
            #                 continue
            #             carseat += seatArrayVec[onCarIndex]
            #             getcar.append(idQueue[onCarIndex])
            #             getindex.append(onCarIndex)
            #             if carseat == MAXSEATNUM6:
            #                 getonthcar.append(flatten(getcar))
            #                 for delgetindex in reversed(getindex):
            #                     del (locQueue[delgetindex])
            #                     del (idQueue[delgetindex])
            #                     del (seatQueue[delgetindex])
            #                 break
            #     return
            # else:
            #     if totalPeople/MAXSEATNUM5 == totalPeople/MAXSEATNUM6:
            #         needCars = totalPeople/MAXSEATNUM5
            #         latQueueIndex = sorted(range(len(outwestLoc)), key=lambda k: outwestLoc[k], cmp=lambda a, b: -1 if a[0] > b[0] else 0)
            #         locQueue = [westorderLoc[locindex] for locindex in latQueueIndex]
            #         idQueue = [westorderID[idindex] for idindex in latQueueIndex]
            #         seatQueue = [westorderSeatNo[seatIndex] for seatIndex in latQueueIndex]
            #         for car in range(needCars):
            #             carseat = 0
            #             getindex = []
            #             getcar = []
            #             seatArrayVec = self.getOrderNumVec(seatQueue)
            #             for onCarIndex in range(len(locQueue)):
            #                 if carseat + seatArrayVec[onCarIndex] > MAXSEATNUM5:
            #                     continue
            #                 carseat += seatArrayVec[onCarIndex]
            #                 getcar.append(idQueue[onCarIndex])
            #                 getindex.append(onCarIndex)
            #                 if carseat == MAXSEATNUM5:
            #                     getonthcar.append(flatten(getcar))
            #                     for delgetindex in reversed(getindex):
            #                         del (locQueue[delgetindex])
            #                         del (idQueue[delgetindex])
            #                         del (seatQueue[delgetindex])
            #                     break
            #         if sum(flatten(seatQueue)) <= 2:
            #             restorderNo += northOrderID + westorderID + idQueue
            #             restorderLoc += northOrderLoc + westorderLoc + locQueue
            #             restorderSeatNo += northOrderSeatnum + westorderSeatNo + seatQueue
            #             return
            #         elif sum(flatten(seatQueue)) <= 4 and sum(flatten(seatQueue)) > 2:
            #             self.anotherCouDingdan(idQueue, locQueue, seatQueue, westorderID, westorderLoc, westorderSeatNo, getonthcar)
            #             restorderNo += northOrderID + westorderID
            #             restorderLoc += northOrderLoc + westorderLoc
            #             restorderSeatNo += northOrderSeatnum + westorderSeatNo
            #             return
            #     else:
            #         needCars = totalPeople/MAXSEATNUM5
            #         sixloops = totalPeople % MAXSEATNUM5
            #         latQueueIndex = sorted(range(len(outwestLoc)), key=lambda k: outwestLoc[k],cmp=lambda a, b: -1 if a[0] > b[0] else 0)
            #         locQueue = [westorderLoc[locindex] for locindex in latQueueIndex]
            #         idQueue = [westorderID[idindex] for idindex in latQueueIndex]
            #         seatQueue = [westorderSeatNo[seatIndex] for seatIndex in latQueueIndex]
            #         for sixcar in range(sixloops):
            #             sixcarseat = 0
            #             sixgetindex = []
            #             sixgetcar = []
            #             sixseatArrayVec = self.getOrderNumVec(seatQueue)
            #             for sixonCarIndex in range(len(locQueue)):
            #                 if sixcarseat + sixseatArrayVec[sixonCarIndex] > MAXSEATNUM6:
            #                     continue
            #                 sixcarseat += sixseatArrayVec[sixonCarIndex]
            #                 sixgetcar.append(idQueue[sixonCarIndex])
            #                 sixgetindex.append(sixonCarIndex)
            #                 if sixcarseat == MAXSEATNUM6:
            #                     getonthcar.append(flatten(sixgetcar))
            #                     for sixdelgetindex in reversed(sixgetindex):
            #                         del (locQueue[sixdelgetindex])
            #                         del (idQueue[sixdelgetindex])
            #                         del (seatQueue[sixdelgetindex])
            #                     break
            #         for five in range(sixloops, needCars):
            #             fivecarseat = 0
            #             fivegetindex = []
            #             fivegetcar = []
            #             fiveseatArrayVec = self.getOrderNumVec(seatQueue)
            #             for fiveonCarIndex in range(len(locQueue)):
            #                 if fivecarseat + fiveseatArrayVec[fiveonCarIndex] > MAXSEATNUM5:
            #                     continue
            #                 fivecarseat += fiveseatArrayVec[fiveonCarIndex]
            #                 fivegetcar.append(idQueue[fiveonCarIndex])
            #                 fivegetindex.append(fiveonCarIndex)
            #                 if fivecarseat == MAXSEATNUM5:
            #                     getonthcar.append(flatten(fivegetcar))
            #                     for fivedelgetindex in reversed(fivegetindex):
            #                         del (locQueue[fivedelgetindex])
            #                         del (idQueue[fivedelgetindex])
            #                         del (seatQueue[fivedelgetindex])
            #                     break
            #         return
            # 当2环到2.5环的订单人数大于6，使用knapsack找5或者6个人，剩下的订单看情况再排班（此方法已被证明不适用）
            # outsideSeatVec = outsideNumVec[outsideIndex]  # 2环外的乘客vec,根据array outsideindex得到与array outsideindex一一对应

    def getwestneighber(self, highoutwest, westVec):
        if len(westVec) == 0:
            return []
        westArray = self.getOrderLocVec(westVec)
        listCenter = [highoutwest]
        listPoints = westArray.tolist()
        if len(westArray) == 1:
            neighborhoodIdx = [0]
            return neighborhoodIdx
        neighborhoodIdx = []  # Put the neighbors of each point here
        neigh = NearestNeighbors(n_neighbors=len(listPoints), metric=auxfn.calcDist)
        neigh.fit(westArray)
        try:
            distances, indices = neigh.kneighbors(listCenter)
        except:
            print 'no west neighbor'
            return neighborhoodIdx
        for index, distance in zip(indices, distances):
            npIndex = index
            npDistance = distance
        for i in range(len(npIndex)):
            if npDistance[i] <= westradius and westVec[npIndex[i]][0] > highoutwest[0]:
                # 已修改，在高纬度增加了必须要大于当前点的纬度
                neighborhoodIdx.append(npIndex[i])
        return neighborhoodIdx

    def getlowwestneighber(self, lowoutwest, westVec):
        if len(westVec) == 0:
            return []
        from recomTimeOnTheBus import eastandwestside
        # 获取当前点到所有订单地点的距离按照从小到大排序
        # 获取当前点到其余所有点的距离
        sd = eastandwestside.SIDE()
        westArray = self.getOrderLocVec(westVec)
        listCenter = [lowoutwest]
        listPoints = westArray.tolist()
        if len(westArray) == 1:
            neighborhoodIdx = [0]
            return neighborhoodIdx
        neighborhoodIdx = []  # Put the neighbors of each point here
        neigh = NearestNeighbors(n_neighbors=len(listPoints), metric=auxfn.calcDist)
        neigh.fit(westArray)
        try:
            distances, indices = neigh.kneighbors(listCenter)
        except:
            print 'no west neighbor'
            return neighborhoodIdx
        for index, distance in zip(indices, distances):
            npIndex = index
            npDistance = distance
        for i in range(len(npIndex)):
            if npDistance[i] <= westradius and westVec[npIndex[i]][0] < lowoutwest[0]:
                # 已修改，在高纬度增加了必须要大于当前点的纬度
                neighborhoodIdx.append(npIndex[i])
                continue
            elif sd.allpick(westVec[npIndex[i]]):
                neighborhoodIdx.append(npIndex[i])
                continue
            elif sd.westpick(westVec[npIndex[i]]):
                neighborhoodIdx.append(npIndex[i])
                continue
        return neighborhoodIdx

    # 当超过7人后按照纬度排班剩下的人数在3,4人凑到5，或者6
    def anotherCouDingdan(self, queueNo, queueLoc, queueSeat, westorderID, westorderLoc, westorderSeatNo, getonthcar):
        outSeats = sum(flatten(queueSeat))
        highneighbor = self.getwestneighber(queueLoc[0], westorderLoc)
        if len(highneighbor) > 0:
            neighbor = highneighbor
        else:
            lowneighbor = self.getlowwestneighber(queueLoc[len(queueLoc) - 1], westorderLoc)
            neighbor = lowneighbor
            if len(neighbor) is 0:
                outcar = flatten(queueNo)
                getonthcar.append(outcar)
                return
        # 西边的订单上车
        westinsidegeton = []
        for nextI in neighbor:
            if outSeats + sum(westorderSeatNo[nextI]) <= 6:
                queueNo.append(westorderID[nextI])
                queueLoc.append(westorderLoc[nextI])
                westinsidegeton.append(nextI)
                outSeats += sum(westorderSeatNo[nextI])
                if outSeats == MAXSEATNUM5 or outSeats == MAXSEATNUM6:
                    outcar = flatten(queueNo)
                    getonthcar.append(outcar)
                    westinsidegeton.sort(cmp=lambda a, b: -1 if a > b else 0)
                    for delinside in westinsidegeton:
                        del (westorderID[delinside])
                        del (westorderLoc[delinside])
                        del (westorderSeatNo[delinside])
                    return
        if len(westinsidegeton) == 0:
            outcar = flatten(queueNo)
            getonthcar.append(outcar)
            return
        else:
            outcar = flatten(queueNo)
            getonthcar.append(outcar)
            westinsidegeton.sort(cmp=lambda a, b: -1 if a > b else 0)
            for delinside in westinsidegeton:
                del (westorderID[delinside])
                del (westorderLoc[delinside])
                del (westorderSeatNo[delinside])
            return

    # 当2环到2.5环的订单为3,4个时寻找西边的订单凑到5个,找到其他区域的的人然后删除，找到后就直接上车
    def coudaofivedingdan(self, outsideIndex, westorderID, westorderLoc, westorderSeatNo, getonthcar):
        outwestID = []      # [[A,,B,C],[D,E,F]]
        outwestLoc = []       # [(lat1,lng1),(lat2,lng2)]
        outwestSeatNo = []
        for outindex in outsideIndex:
            outwestID.append(westorderID[outindex])
            outwestLoc.append(westorderLoc[outindex])
            outwestSeatNo.append(westorderSeatNo[outindex])
        outSeats = sum(flatten(outwestSeatNo))
        for outdelinx in reversed(outsideIndex):
            del (westorderID[outdelinx])
            del (westorderLoc[outdelinx])
            del (westorderSeatNo[outdelinx])
        # 根据高纬度到低纬度排序，lat为loc的第一个参数
        locSoted = sorted(outwestLoc, cmp=lambda a, b: -1 if a[0] > b[0] else 0)
        highneighbor = self.getwestneighber(locSoted[0], westorderLoc)
        if len(highneighbor) > 0:
            neighbor = highneighbor
        else:
            lowneighbor = self.getlowwestneighber(locSoted[len(locSoted)-1], westorderLoc)
            neighbor = lowneighbor
            if len(neighbor) is 0:
                carpool = [wd for (lc, wd) in sorted(zip([lat[0] for lat in outwestLoc], outwestID), reverse=True)]
                outcar = flatten(carpool)
                getonthcar.append(outcar)
                return
        # 西边的订单上车
        westinsidegeton = []
        for nextI in neighbor:
            if outSeats + sum(westorderSeatNo[nextI]) <= 6:
                outwestID.append(westorderID[nextI])
                outwestLoc.append(westorderLoc[nextI])
                westinsidegeton.append(nextI)
                outSeats += sum(westorderSeatNo[nextI])
                if outSeats == MAXSEATNUM5 or outSeats == MAXSEATNUM6:
                    carpool = [wd for (lc, wd) in sorted(zip([lat[0] for lat in outwestLoc], outwestID), reverse=True)]
                    outcar = flatten(carpool)
                    getonthcar.append(outcar)
                    westinsidegeton.sort(cmp=lambda a, b: -1 if a > b else 0)
                    for delinside in westinsidegeton:
                        del (westorderID[delinside])
                        del (westorderLoc[delinside])
                        del (westorderSeatNo[delinside])
                    return
        if len(westinsidegeton) == 0:
            carpool = [wd for (lc, wd) in sorted(zip([lat[0] for lat in outwestLoc], outwestID), reverse=True)]
            outcar = flatten(carpool)
            getonthcar.append(outcar)
            return
        else:
            carpool = [wd for (lc, wd) in sorted(zip([lat[0] for lat in outwestLoc], outwestID), reverse=True)]
            outcar = flatten(carpool)
            getonthcar.append(outcar)
            westinsidegeton.sort(cmp=lambda a, b: -1 if a > b else 0)
            for delinside in westinsidegeton:
                del (westorderID[delinside])
                del (westorderLoc[delinside])
                del (westorderSeatNo[delinside])
            return

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



