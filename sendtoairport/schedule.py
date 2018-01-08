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
# 内部引用
import knapsack
import auxfn
import mapAPI
from recomTimeOnTheBus import eastandwestside
from recomTimeOnTheBus import getneighbor

# BMAPAIRPORTCOORDINATE = [30.574590, 103.955020]
MAXSEATNUM5 = 5
MAXSEATNUM6 = 6
NORTH = 30.604043
# CHENGDULAT = 30.6
# LONGDISlIMT = 4500
# SEARCHLOOP = 500
# 经度分割(百度)
longDistinguish = 104.074086
# 西北边3000米
westradius = 3000


class DIST:

    def getTheSpecifyAndNormal(self, normalPassengerDic, resdict):
        # 创建list来保存指定司机的订单
        specifyDriverDic = []
        for element in resdict:
            if 'driver' not in element.keys() or element['driver'] is None or element['driver'] is u"":
                normalPassengerDic.append(element)
            else:
                specifyDriverDic.append(element)
        return specifyDriverDic

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
    def getTheSpecifyDriverOrder(self, specifyDriverDic):
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
            if seatnum == MAXSEATNUM5 or seatnum == MAXSEATNUM6:
                carSpecifyList.append([poid])
                continue
            else:
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
                sixdel = []
                tmpspecialID = copy.copy(getSpecifyID[i])
                tmpspecialseats = copy.copy(getSpecifySN[i])
                # for seatidx in range(len(tmpspecialseats)):
                #     if tmpspecialseats[seatidx] >= 5:
                #         carSpecifyList.append([tmpspecialID[seatidx]])
                #         sixdel.append(seatidx)
                # for sl in reversed(sixdel):
                #     del(tmpspecialID[sl])
                #     del (tmpspecialseats[sl])
                allseatnums = sum(tmpspecialseats)
                # if allseatnums <= MAXSEATNUM6:
                #     carSpecifyList.append(tmpspecialID)
                #     continue
                needcar = allseatnums/MAXSEATNUM6
                leftpas = allseatnums % MAXSEATNUM6
                if leftpas == 0:  # 刚好能坐整数辆车
                    for n in range(needcar):
                        sixpassengeer = knapsack.zeroOneKnapsack(tmpspecialseats, MAXSEATNUM6)
                        storeindex = [j for j, x in enumerate(sixpassengeer[1]) if x == 1]
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
                        mstoreindex = [k for k, l in enumerate(averagepass[1]) if l == 1]
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

    # 初步处理数据，传入json字符串resdict,订单人数=5/6的存入提前上车的数组advancegetonthecar
    def getAllRepeatData(self, advanceGetOnTheCar, normalPassengerDic):
        repeatdicInfo = []
        for i in range(len(normalPassengerDic)):
            orderdict = {}
            seatnum = normalPassengerDic[i]['seatnum']
            if seatnum == 6 or seatnum == 5:
                advanceGetOnTheCar.append([normalPassengerDic[i]['BID']])
            else:
                bdlat = round(normalPassengerDic[i]['bdlat'], 6)
                bdlng = round(normalPassengerDic[i]['bdlng'], 6)
                orderdict['loc'] = (bdlat, bdlng)
                orderdict['bid'] = [normalPassengerDic[i]['BID']]
                orderdict['seatno'] = [seatnum]
                repeatdicInfo.append(orderdict)
        return repeatdicInfo
        # for element in normalPassengerDic:
        #     tmp = []
        #     bdLat = element['bdlat']
        #     bdLng = element['bdlng']
        #     loc = auxfn.BD2AMap(bdLat, bdLng)
        #     gglat = round(loc.lat, 6)
        #     gglng = round(loc.lng, 6)
        #     poid = element['BID']
        #     seatnum = element['seatnum']
        #     tmp.append(gglat)
        #     tmp.append(gglng)
        #     if seatnum is 6 or seatnum is 5:
        #         getonthecar.append([poid])
        #         getonthecarloc.append(tuple(tmp))
        #         getonthecarseatnum.append([seatnum])
        #     else:
        #         repeatpoid.append(poid)
        #         repeatseatnum.append(seatnum)
        #         repeatloc.append(tuple(tmp))

    # 合并订单：100m范围
    def getDuplicateData(self, repeatdicInfo):
        # duplicateLoc = list(set(repeatloc))
        # for element in duplicateLoc:
        #     repeat = auxfn.getAllIndices(element, repeatloc)
        #     orderidtmp = []
        #     seatnumtmp = []
        #     for element1 in repeat:
        #         orderidtmp.append(repeatOrderID[element1])
        #         seatnumtmp.append(repeatSeatnum[element1])
        #     duplicateOrderid.append(orderidtmp)
        #     duplicateSeatNum.append(seatnumtmp)
        allLoopsTimes = len(repeatdicInfo)
        for i in range(allLoopsTimes):
            tmpindex = []
            # 如果全部只剩一个元素了，那么就直接合并结束循环
            if len(repeatdicInfo) == 1:
                break
            # 如果剩下的元素大于一个那么i为最后一个元素就结束循环
            if i == len(repeatdicInfo)-1:
                break
            for sameindex in range(i+1, len(repeatdicInfo)):
                pointdistance = auxfn.calcDist(repeatdicInfo[i]['loc'], repeatdicInfo[sameindex]['loc'])
                if pointdistance <= 100:
                    tmpindex.append(sameindex)
            # 将在100m范围内的信息添加到一起
            if len(tmpindex) > 0:
                for el in tmpindex:
                    repeatdicInfo[i]['bid'] += repeatdicInfo[el]['bid']
                    repeatdicInfo[i]['seatno'] += repeatdicInfo[el]['seatno']
                for delindex in reversed(tmpindex):
                    del (repeatdicInfo[delindex])
        duplicateLoc = copy.copy(repeatdicInfo)
        return duplicateLoc

    # 排除一个地点中=5/6的情况，如果这个地点人数大于6，那么将订单人数相加=5/6存入getonthecar，剩下的订单存入RMMTSID，RMMTSLoc
    def removeMoreThanSixPassenger(self, rmtspID, rmtspLoc, rmtspSeat, duplicateInfo, advanceGetOnTheCar):
        for i in range(len(duplicateInfo)):
            if sum(duplicateInfo[i]['seatno']) == MAXSEATNUM6 or sum(duplicateInfo[i]['seatno']) == MAXSEATNUM5:
                advanceGetOnTheCar.append(duplicateInfo[i]['bid'])
            elif sum(duplicateInfo[i]['seatno']) > MAXSEATNUM6:
                tmpSeatnum = copy.copy(duplicateInfo[i]['seatno'])
                tmpID = copy.copy(duplicateInfo[i]['bid'])
                knapsack6 = knapsack.zeroOneKnapsack(tmpSeatnum, MAXSEATNUM6)
                knapsack5 = knapsack.zeroOneKnapsack(tmpSeatnum, MAXSEATNUM5)
                while knapsack6[0] == MAXSEATNUM6 or knapsack5[0] == MAXSEATNUM5:
                    if knapsack6[0] == 6:
                        knapsackvalue = knapsack6[1]
                    else:
                        knapsackvalue = knapsack5[1]
                    tmpalreadygetonthcarid = []
                    storeindex = [j for j, x in enumerate(knapsackvalue) if x == 1]      # 列表推导式
                    for element1 in storeindex:
                        tmpalreadygetonthcarid.append(tmpID[element1])
                    advanceGetOnTheCar.append(tmpalreadygetonthcarid)
                    for element2 in reversed(storeindex):
                        del (tmpSeatnum[element2])
                        del (tmpID[element2])
                    if len(tmpSeatnum) > 1:
                        knapsack6 = knapsack.zeroOneKnapsack(tmpSeatnum, MAXSEATNUM6)
                        knapsack5 = knapsack.zeroOneKnapsack(tmpSeatnum, MAXSEATNUM5)
                    elif len(tmpSeatnum) == 1:
                        rmtspID.append(tmpID)
                        rmtspLoc.append(duplicateInfo[i]['loc'])
                        rmtspSeat.append(tmpSeatnum)
                        break
                    else:
                        break
                else:
                    if sum(tmpSeatnum) < 6:
                        rmtspID.append(tmpID)
                        rmtspLoc.append(duplicateInfo[i]['loc'])
                        rmtspSeat.append(tmpSeatnum)
                    else:                                       # 增加同一个地点大于6个人订单情况
                        tmpLoc = list(duplicateInfo[i]['loc'])
                        r = 0
                        for k in xrange(len(tmpID)):
                            tmpLoc[0] += r
                            tmpLoc[1] += r
                            rmtspID.append([tmpID[k]])
                            rmtspLoc.append(tuple(tmpLoc))
                            rmtspSeat.append([tmpSeatnum[k]])
                            r += 0.00001
            else:
                rmtspID.append(duplicateInfo[i]['bid'])
                rmtspLoc.append(duplicateInfo[i]['loc'])
                rmtspSeat.append(duplicateInfo[i]['seatno'])

    # 如果已经上车的且订单中人数=5，那么寻找它500米范围内的一个人，如果有就上车且在RMMSID、RMMSLoc、RMMTSseatnum中删除订单信息，如果没有就什么不做
    # 已经不再使用
    def getTheFivePersonAroundOnlyOne(self, getonthecar, getonthecarloc, getonthecarseatnum, RMMTSID, RMMTSLoc, RMMTSseatnum):
        tmpRMMTSLoc = copy.copy(RMMTSLoc)
        tmpRMMTSLocVec = self.getOrderLocVec(tmpRMMTSLoc)
        frelement = []
        for i in range(len(getonthecarseatnum)):
            if sum(getonthecarseatnum[i]) == MAXSEATNUM5:   # 修改==为is提高效率
                arounddistvec = auxfn.calcDistVec(getonthecarloc[i], tmpRMMTSLocVec)
                tmpix = np.where(arounddistvec < 501)  # 寻找500米的范围
                if len(tmpix[0]) is not 0:
                    ix = [x for x in tmpix[0] if x not in frelement]
                    if len(ix) is not 0:
                        for element in ix:
                            if len(RMMTSseatnum[element]) == 1 and RMMTSseatnum[element][0] == 1:
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
    # 计算所有订单的直线距离
    # def checkLongdiscondition(self, currenPasIdxVec, allOrderLoc, nexpasIdx):
    #     nextpassenger = []
    #     for i in xrange(len(nexpasIdx)):
    #         longDist = 0
    #         if len(currenPasIdxVec) == 1:
    #             longDist += auxfn.calcDist((CHENGDULAT, allOrderLoc[currenPasIdxVec[0]][1]), (CHENGDULAT, allOrderLoc[nexpasIdx[i]][1]))
    #         else:
    #             for j in xrange(len(currenPasIdxVec)):
    #                 longDist += auxfn.calcDist((CHENGDULAT, allOrderLoc[currenPasIdxVec[j]][1]), ((CHENGDULAT, allOrderLoc[currenPasIdxVec[j+1]][1])))
    #                 if j+1 == len(currenPasIdxVec)-1:
    #                     longDist += auxfn.calcDist((CHENGDULAT, allOrderLoc[currenPasIdxVec[j+1]][1]), (CHENGDULAT, allOrderLoc[nexpasIdx[i]][1]))
    #                     break
    #         if longDist <= LONGDISlIMT:
    #             nextpassenger.append(nexpasIdx[i])
    #     return nextpassenger

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
    # def gethasgotonthecartimedistance(self, getonthecarloc, getonthecarorderid):
    #     GTI = mapAPI.AMapAPI()
    #     if len(getonthecarloc) is not 1:
    #         orderVec = self.getOrderLocVec(getonthecarloc)
    #         orderNum = len(orderVec)
    #     else:
    #         orderVec = np.array([getonthecarloc[0][0], getonthecarloc[0][1]])
    #         orderNum = len(getonthecarloc)
    #     timedistancevec = GTI.getTimeDistVec(BMAPAIRPORTCOORDINATE, orderVec, orderNum)
    #     hasgetonthecarorderandtime = []    # [[[a,878],[b,788],[c,898]],[[d,658],[e,345]]]
    #     for i in range(orderNum):
    #         car = []
    #         for j in range(len(getonthecarorderid[i])):
    #             tmp = []
    #             tmp.append(getonthecarorderid[i][j])
    #             tmp.append(timedistancevec[i])
    #             car.append(tmp)
    #         hasgetonthecarorderandtime.append(car)
    #     return hasgetonthecarorderandtime

    # 超过7人排班后剩下的人中排班
    def anothereastcourn(self, allid, allloc, allseatNo, eastoutID, eastoutLoc, eastoutseatNo, getonthecar):
        sd = eastandwestside.SIDE()
        getcarNum = sum(flatten(eastoutseatNo))
        # 优先寻找特殊接送区域的人
        # 在剩下的所有人中寻找在特殊区域的人
        allpickindex = [ap for ap in range(len(allloc)) if sd.allpick(allloc[ap])]
        eastpickindex = [ep for ep in range(len(allloc)) if sd.eastpick(allloc[ep])]
        eastgetcaridx = []
        # 优先选择所有可以接送的区域
        if len(allpickindex) > 0:
            for apd in allpickindex:
                if getcarNum + sum(allseatNo[apd]) <= 6:
                    eastgetcaridx.append(apd)
                    eastoutID.append(allid[apd])
                    eastoutLoc.append(allloc[apd])
                    eastoutseatNo.append(allseatNo[apd])
                    getcarNum += sum(allseatNo[apd])
                else:
                    break
            if getcarNum == MAXSEATNUM5 or getcarNum == MAXSEATNUM6:
                # 按照纬度由高到低排序
                acar = [wd for (lc, wd) in sorted(zip([lat[0] for lat in eastoutLoc], eastoutID), reverse=True)]
                getonthecar.append(flatten(acar))
                # 删除已经上车的订单
                for delid in reversed(eastgetcaridx):
                    del (allid[delid])
                    del (allloc[delid])
                    del (allseatNo[delid])
                return
        # 人没有装满继续选择西边可接送区域
        if len(eastpickindex) > 0:
            for epd in eastpickindex:
                if getcarNum + sum(allseatNo[epd]) <= 6:
                    eastgetcaridx.append(epd)
                    eastoutID.append(allid[epd])
                    eastoutLoc.append(allloc[epd])
                    eastoutseatNo.append(allseatNo[epd])
                    getcarNum += sum(allseatNo[epd])
                else:
                    break
            if getcarNum == MAXSEATNUM5 or getcarNum == MAXSEATNUM6:
                # 按照纬度由高到低排序
                acar = [wd for (lc, wd) in sorted(zip([lat[0] for lat in eastoutLoc], eastoutID), reverse=True)]
                getonthecar.append(flatten(acar))
                # 删除已经上车的订单
                for delid in reversed(eastgetcaridx):
                    del (allid[delid])
                    del (allloc[delid])
                    del (allseatNo[delid])
                return
        # 如果人没有装满那么继续寻找离得比较近的和纬度比自己高的
        locSoted = sorted(eastoutLoc, cmp=lambda a, b: -1 if a[0] > b[0] else 0)
        getneighidx = self.getwestneighber(locSoted[0], allloc)
        notgetneighbor = list(set(getneighidx) - set(eastgetcaridx))
        if len(notgetneighbor) == 0:
            for deleg in reversed(eastgetcaridx):
                del (allid[deleg])
                del (allloc[deleg])
                del (allseatNo[deleg])
            # 已确定不进入排班
            if getcarNum <= 2:
                # 进入所有订单的自动排班，不上车
                allid += eastoutID
                allloc += eastoutLoc
                allseatNo += eastoutseatNo
            else:
                acar = [wd for (lc, wd) in sorted(zip([lat[0] for lat in eastoutLoc], eastoutID), reverse=True)]
                getonthecar.append(flatten(acar))
                return
        else:
            for ngb in notgetneighbor:
                if getcarNum + sum(allseatNo[ngb]) <= 6:
                    eastgetcaridx.append(ngb)
                    eastoutID.append(allid[ngb])
                    eastoutLoc.append(allloc[ngb])
                    eastoutseatNo.append(allseatNo[ngb])
                    getcarNum += sum(allseatNo[ngb])
                else:
                    break
            for delngb in sorted(eastgetcaridx, reverse=True):
                del (allid[delngb])
                del (allloc[delngb])
                del (allseatNo[delngb])
            if getcarNum <= 2:
                # 进入所有订单的自动排班，不上车
                allid += eastoutID
                allloc += eastoutLoc
                allseatNo += eastoutseatNo
            else:
                acar = [wd for (lc, wd) in sorted(zip([lat[0] for lat in eastoutLoc], eastoutID), reverse=True)]
                getonthecar.append(flatten(acar))
            return

    def eastcouren(self, allid, allloc, allseatNo, outindex, getonthecar):
        sd = eastandwestside.SIDE()
        # 将在2环到2.5环的人单独提出来
        eastoutID = []
        eastoutLoc = []
        eastoutseatNo = []
        for i in outindex:
            eastoutID.append(allid[i])  # [[a,b],[]]
            eastoutLoc.append(allloc[i])  # [(lat,lng)]
            eastoutseatNo.append(sum(allseatNo[i]))  # [2,1,1]
        # 在总的订单中删除要提前上车的乘客
        for deli in reversed(outindex):
            del (allid[deli])
            del (allloc[deli])
            del (allseatNo[deli])
        getcarNum = sum(eastoutseatNo)
        # 优先寻找特殊接送区域的人
        # 在剩下的所有人中寻找在特殊区域的人
        allpickindex = [ap for ap in range(len(allloc)) if sd.allpick(allloc[ap])]
        eastpickindex = [ep for ep in range(len(allloc)) if sd.eastpick(allloc[ep])]
        eastgetcaridx = []
        # 优先选择所有可以接送的区域
        if len(allpickindex) > 0:
            for apd in allpickindex:
                if getcarNum+sum(allseatNo[apd]) <= 6:
                    eastgetcaridx.append(apd)
                    eastoutID.append(allid[apd])
                    eastoutLoc.append(allloc[apd])
                    eastoutseatNo.append(sum(allseatNo[apd]))
                    getcarNum += sum(allseatNo[apd])
                else:
                    break
            if getcarNum == MAXSEATNUM5 or getcarNum == MAXSEATNUM6:
                # 按照纬度由高到低排序
                acar = [wd for (lc, wd) in sorted(zip([lat[0] for lat in eastoutLoc], eastoutID), reverse=True)]
                getonthecar.append(flatten(acar))
                # 删除已经上车的订单
                for delid in reversed(eastgetcaridx):
                    del (allid[delid])
                    del (allloc[delid])
                    del (allseatNo[delid])
                return
        # 人没有装满继续选择西边可接送区域
        if len(eastpickindex) > 0:
            for epd in eastpickindex:
                if getcarNum+sum(allseatNo[epd]) <= 6:
                    eastgetcaridx.append(epd)
                    eastoutID.append(allid[epd])
                    eastoutLoc.append(allloc[epd])
                    eastoutseatNo.append(sum(allseatNo[epd]))
                    getcarNum += sum(allseatNo[epd])
                else:
                    break
            if getcarNum == MAXSEATNUM5 or getcarNum == MAXSEATNUM6:
                # 按照纬度由高到低排序
                acar = [wd for (lc, wd) in sorted(zip([lat[0] for lat in eastoutLoc], eastoutID), reverse=True)]
                getonthecar.append(flatten(acar))
                # 删除已经上车的订单
                for delid in reversed(eastgetcaridx):
                    del (allid[delid])
                    del (allloc[delid])
                    del (allseatNo[delid])
                return
        # 如果人没有装满那么继续寻找离得比较近的和纬度比自己高的
        locSoted = sorted(eastoutLoc, cmp=lambda a, b: -1 if a[0] > b[0] else 0)
        getneighidx = self.getwestneighber(locSoted[0], allloc)
        notgetneighbor = list(set(getneighidx)-set(eastgetcaridx))
        if len(notgetneighbor) == 0:
            for deleg in reversed(eastgetcaridx):
                del(allid[deleg])
                del(allloc[deleg])
                del(allseatNo[deleg])
            # 待商量cdh
            if getcarNum <= 2:
                # 进入所有订单的自动排班，不上车
                allid += eastoutID
                allloc += eastoutLoc
                allseatNo += [[seat] for seat in eastoutseatNo]
            else:
                acar = [wd for (lc, wd) in sorted(zip([lat[0] for lat in eastoutLoc], eastoutID), reverse=True)]
                getonthecar.append(flatten(acar))
            return
        else:
            for ngb in notgetneighbor:
                if getcarNum + sum(allseatNo[ngb]) <= 5:
                    eastgetcaridx.append(ngb)
                    eastoutID.append(allid[ngb])
                    eastoutLoc.append(allloc[ngb])
                    eastoutseatNo.append(sum(allseatNo[ngb]))
                    getcarNum += sum(allseatNo[ngb])
                else:
                    break
            for delngb in sorted(eastgetcaridx, reverse=True):
                del(allid[delngb])
                del(allloc[delngb])
                del(allseatNo[delngb])
            if getcarNum <= 2:
                # 进入所有订单的自动排班，不上车
                allid += eastoutID
                allloc += eastoutLoc
                allseatNo += [[seat] for seat in eastoutseatNo]
            else:
                acar = [wd for (lc, wd) in sorted(zip([lat[0] for lat in eastoutLoc], eastoutID), reverse=True)]
                getonthecar.append(flatten(acar))
            return

    def eastschedule(self, northOrderID, northOrderLoc, northOrderSeatnum, getonthcar):
        sd = eastandwestside.SIDE()
        eastoutsideNo = sd.ateast2out(northOrderLoc, len(northOrderLoc))
        eastOutSideIndex = np.where(eastoutsideNo <= 1)[0]  # 在2环和2.5环之间的index
        if len(eastOutSideIndex) == 0:
            return
        eastOutSideNumVec = self.getOrderNumVec(northOrderSeatnum)  # 二维的乘客人数转换为与地点对应的一维数组 array[3,1]
        if sum(eastOutSideNumVec[eastOutSideIndex]) == 5 or sum(eastOutSideNumVec[eastOutSideIndex]) == 6:
            callcar = []
            callloc = []
            for out in eastOutSideIndex:
                callcar.append(northOrderID[out])
                callloc.append(northOrderLoc[out])
            # 两个列表的排序，car的顺序是有loc中lat的顺序决定的
            acar = [wd for (lc, wd) in sorted(zip([lat[0] for lat in callloc], callcar), reverse=True)]
            getonthcar.append(flatten(acar))
            for delout in reversed(eastOutSideIndex):
                del (northOrderID[delout])
                del (northOrderLoc[delout])
                del (northOrderSeatnum[delout])
            return
        elif sum(eastOutSideNumVec[eastOutSideIndex]) <= 4:
            self.eastcouren(northOrderID, northOrderLoc, northOrderSeatnum, eastOutSideIndex, getonthcar)
            return
        else:
            # 处理东边大于6个人的情况
            outeastID = []  # [[A,,B,C],[D,E,F]]
            outeastLoc = []  # [(lat1,lng1),(lat2,lng2)]
            outeastSeatNo = []  # [[1,1,1], [2,1,1]]
            for outindex in eastOutSideIndex:
                outeastID.append(northOrderID[outindex])
                outeastLoc.append(northOrderLoc[outindex])
                outeastSeatNo.append(northOrderSeatnum[outindex])
            for outdelinx in reversed(eastOutSideIndex):
                del (northOrderID[outdelinx])
                del (northOrderLoc[outdelinx])
                del (northOrderSeatnum[outdelinx])
            # 按照纬度拍一个顺序
            latQueueIndex = sorted(range(len(outeastLoc)), key=lambda k: outeastLoc[k], cmp=lambda a, b: -1 if a[0] > b[0] else 0)
            locQueue = [outeastLoc[locindex] for locindex in latQueueIndex]
            idQueue = [outeastID[idindex] for idindex in latQueueIndex]
            seatQueue = [outeastSeatNo[seatIndex] for seatIndex in latQueueIndex]
            outsideSeatVec = self.getOrderNumVec(seatQueue)
            while sum(outsideSeatVec) >= MAXSEATNUM5:
                getcarIndex = []
                tmpcar = []
                tmploc = []
                carSeat = 0
                for i in range(len(idQueue)):
                    if carSeat + outsideSeatVec[i] > MAXSEATNUM6:
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
                                del (locQueue[deli])
                                del (idQueue[deli])
                                del (seatQueue[deli])
                            break
                        else:
                            try:
                                if carSeat + outsideSeatVec[i + 1] == MAXSEATNUM6:
                                    tmpcar.append(idQueue[i + 1])
                                    tmploc.append(locQueue[i + 1])
                                    getcarIndex.append(i + 1)
                                    carpool = [wd for (lc, wd) in
                                               sorted(zip([lat[0] for lat in tmploc], tmpcar), reverse=True)]
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
            if sum(outsideSeatVec) > 0:
                self.anothereastcourn(northOrderID, northOrderLoc, northOrderSeatnum, idQueue, locQueue, seatQueue, getonthcar)
                return

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
        if len(outsideIndex) == 0:
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
            print 'no neighbor'
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
        westarealoclist = []  # 每个idx对应的区域范围
        for loc in westorderLoc:
            areanum = getneighbor.findtheareanumber(loc[0], loc[1])
            westarealoclist.append(areanum)
        area26 = [16, 19, 21, 23, 26]
        neighborareaidx = getneighbor.getthewestneighbor(area26, westarealoclist, westorderLoc)
        if len(neighborareaidx) > 0:
            outSeats = sum(flatten(queueSeat))
            # 西边的订单上车
            westinsidegeton = []
            for nextI in neighborareaidx:
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
        else:
            outcar = flatten(queueNo)
            getonthcar.append(outcar)
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
        # 修改为接路边上的点
        westarealoclist = []  # 每个idx对应的区域范围
        for loc in westorderLoc:
            areanum = getneighbor.findtheareanumber(loc[0], loc[1])
            westarealoclist.append(areanum)
        area26 = [16, 19, 21, 23, 26]
        neighborareaidx = getneighbor.getthewestneighbor(area26, westarealoclist, westorderLoc)
        if len(neighborareaidx) > 0:
            westinsidegeton = []
            for nextI in neighborareaidx:
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
        else:
            carpool = [wd for (lc, wd) in sorted(zip([lat[0] for lat in outwestLoc], outwestID), reverse=True)]
            outcar = flatten(carpool)
            getonthcar.append(outcar)
            return

    # 对区域内的点进行到当前点的距离的排序选取一个最小的点
    def getthesameareapointdistance(self, arealoclist, firstPassengerIdx, currentarea, allgetonthecaridx, restorderLoc):
        neighborareaindex = [a for a in range(len(arealoclist)) if arealoclist[a] == currentarea and a not in allgetonthecaridx]
        neighborareaindexlength = len(neighborareaindex)
        if neighborareaindexlength == 0:
            return None
        elif neighborareaindexlength == 1:
            return neighborareaindex
        elif neighborareaindexlength > 1:
            neighborloc = [restorderLoc[locidx] for locidx in neighborareaindex]
            neighborlocvec = self.getOrderLocVec(neighborloc)  # 一维的经纬度列表转换为二维的经纬度数组
            locdisvec = auxfn.calcDistVec(restorderLoc[firstPassengerIdx], neighborlocvec)
            # 对当前区域到当前点的距离排序得到的排序后的index
            locsortidx = [idx for (loc, idx) in sorted(zip(locdisvec, neighborareaindex))]
            return locsortidx

    def quescheduel(self, carOrderList, restorderNo, restorderLoc):
        jichang = [30.599722, 104.04031]  # 机场
        newcaorderlsit = []
        carloclist = []
        for car in carOrderList:
            tmploclist = []
            for order in car:
                for i in range(len(restorderLoc)):
                    if order in restorderNo[i]:
                        tmploclist.append(restorderLoc[i])
            carloclist.append(tmploclist)
        # carorderlist 和 carloclist现在是一一对应的了
        for element in range(len(carOrderList)):
            numorder = len(carOrderList[element])
            if numorder > 2:
                waitlist = copy.copy(carloclist[element])
                orderVec = self.getOrderLocVec(waitlist)
                distDistVec = auxfn.calcDistVec(jichang, orderVec)
                currentpointidx = np.argsort(distDistVec)[::-1][0]
                quenelsit = [currentpointidx]
                for n in range(len(waitlist)):
                    distDistVec = auxfn.calcDistVec(waitlist[currentpointidx], orderVec)
                    getthesortedindex = np.argsort(distDistVec)
                    notgetindex = getthesortedindex[np.in1d(getthesortedindex, quenelsit, invert=True)]
                    quenelsit.append(notgetindex[0])
                    if len(waitlist) == 2:
                        break
                    currentpointidx = notgetindex[0]
                    if len(waitlist) - len(quenelsit) == 1:
                        quenelsit.append(notgetindex[1])
                        break
                # from tsp_solver.greedy import solve_tsp
                # solve_tsp problem 
                # waitdisvec = np.zeros([numorder, numorder])
                # for i in range(numorder):
                #     for j in range(numorder):
                #         waitdisvec[i, j] = auxfn.calcDist(waitlist[i], waitlist[j])
                # bestpath = solve_tsp(waitdisvec)
                tmpneworderlist = [carOrderList[element][tpno] for tpno in quenelsit]
                newcaorderlsit.append(tmpneworderlist)
            else:
                newcaorderlsit.append(carOrderList[element])
        return newcaorderlsit






