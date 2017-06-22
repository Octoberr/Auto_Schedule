# coding:utf-8
"""
Wangmeng song
June 9,2017

"""
import json

from itertools import groupby
from operator import itemgetter
from sendtoairport import StartSchedule


# 将订单信息转换为json数组[{numberoforder:3,OrderInfos:[{orderpoid:gfg,duration:1800},{orderpoid:jhj,duration:1800}]},{....}]
def incodejs(timepointVec, scheduleDataVec):
    car = []
    for i in xrange(len(timepointVec)):
        for element in scheduleDataVec[i]:
            d = {}
            d['numberoforder'] = len(element)
            ord = []
            for element2 in element:
                f = {}
                f['BID'] = element2[0]
                f['duration'] = element2[1]
                f['timetable'] = timepointVec[i]
                ord.append(f)
            d['OrderInfos'] = ord
            car.append(d)
    jsondatar = json.dumps(car, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return jsondatar
# def incodejs(AllscheduleData, scheduleDataVec):
#     car = []
#     tmpIdx = 1
#     for element4 in scheduleDataVec:
#         for element1 in element4:
#             for element2 in element1:
#                 for element3 in AllscheduleData:
#                     if element2[0] == element3['BID']:
#                         f = {}
#                         f["orderNum"] = element3['BID']
#                         f["lng"] = element3['bdlng']
#                         f["lat"] = element3['bdlat']
#                         f["idx"] = tmpIdx
#                         car.append(f)
#             tmpIdx = tmpIdx + 1
#     jsondatar = json.dumps(car, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
#     return jsondatar


def geteachTimepointSchedule(AllscheduleData):
    AllscheduleData = sorted(AllscheduleData, key=itemgetter('date'))
    allDataGroups = groupby(AllscheduleData, key=itemgetter('date'))
    timepointVec = []
    scheduleDataVec = []  # [[[[],[],[]],[]]]
    for today, todaydata in allDataGroups:
        todayScheduleData = list(todaydata)
        todayScheduleData = sorted(todayScheduleData, key=itemgetter('timetable'))
        groups = groupby(todayScheduleData, key=itemgetter('timetable'))
        for key, value in groups:
            timepointVec.append(key)
            timepointorder = list(value)
            if len(timepointorder) > 1:
                scheduleDataVec.append(StartSchedule.startschedul(timepointorder))
            else:
                onlyone = [[[timepointorder[0]['BID'], 0]]]
                scheduleDataVec.append(onlyone)
    # jsondata = incodejs(AllscheduleData, scheduleDataVec)
    jsondata = incodejs(timepointVec, scheduleDataVec)
    return jsondata



