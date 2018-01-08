# coding:utf-8
"""
creat by swm 2017 10 19
描述：
提供打乱分组后最优路径的选择
"""
import numpy as np
import auxfn
import copy
import json


def getOrderLocVec(orderLocList):
    orderLocVec = np.zeros([len(orderLocList), 2], dtype=float)
    for i in range(len(orderLocList)):
        orderLocVec[i][0] = orderLocList[i][0]
        orderLocVec[i][1] = orderLocList[i][1]
    return orderLocVec


def incodejs(newcaorderlsit):
    car = []
    for i in xrange(len(newcaorderlsit)):
        f = {}
        tmpcar = []
        for j in range(len(newcaorderlsit[i])):
            d = {}
            d['sequence'] = j
            d['BID'] = newcaorderlsit[i][j]
            tmpcar.append(d)
        f['OrderInfos'] = tmpcar
        car.append(f)
    jsondatar = json.dumps(car, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return jsondatar


# 2 送机
def TheShortestPath(jsonargs):
    jichang = [30.599722, 104.04031]  # 机场
    newcaorderlsit = []
    ordernum = []
    orderloc = []
    for car in jsonargs:
        ordertmp = []
        loctmp = []
        for order in car['orderinfos']:
            ordertmp.append(order['BID'])
            loctmp.append((order['bdlat'], order['bdlng']))
        ordernum.append(ordertmp)
        orderloc.append(loctmp)
    # 得到ordernum和orderloc一一对应的数组
    for element in range(len(ordernum)):
        if len(orderloc[element]) > 1:
            waitlist = copy.copy(orderloc[element])
            orderVec = getOrderLocVec(waitlist)
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
            tmpneworderlist = [ordernum[element][tpno] for tpno in quenelsit]
            newcaorderlsit.append(tmpneworderlist)
        else:
            newcaorderlsit.append(ordernum[element])
    jsondata = incodejs(newcaorderlsit)
    return jsondata


# 1 接机
def HomeShortestPath(jsonargs):
    BMAPAIRPORTCOORDINATE = [30.574590, 103.955020]
    newcaorderlsit = []
    ordernum = []
    orderloc = []
    for car in jsonargs:
        # 按照纬度排一个顺序
        # latQueueIndex = sorted(range(len(car)), key=lambda k: car[k],
        #                        cmp=lambda a, b: -1 if a['bdlat'] > b['bdlat'] else 0)
        ordertmp = []
        loctmp = []
        for order in car['orderinfos']:
            ordertmp.append(order['BID'])
            loctmp.append((order['bdlat'], order['bdlng']))
        ordernum.append(ordertmp)
        orderloc.append(loctmp)
    # 得到ordernum和orderloc一一对应的数组
    for element in range(len(ordernum)):
        if len(orderloc[element]) > 1:
            waitlist = copy.copy(orderloc[element])
            orderVec = getOrderLocVec(waitlist)
            distDistVec = auxfn.calcDistVec(BMAPAIRPORTCOORDINATE, orderVec)
            currentpointidx = np.argmin(distDistVec)
            quenelsit = []
            quenelsit.append(currentpointidx)
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
            tmpneworderlist = [ordernum[element][tpno] for tpno in quenelsit]
            newcaorderlsit.append(tmpneworderlist)
        else:
            newcaorderlsit.append(ordernum[element])
    jsondata = incodejs(newcaorderlsit)
    return jsondata
