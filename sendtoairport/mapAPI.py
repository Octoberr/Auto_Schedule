# coding:utf-8

"""
Donghui Chen, Wangmeng Song
May 15, 2017
"""

import json
import requests
import socket
import numpy as np
from retrying import retry

BROWSER = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 ' \
          '(KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36'
HEADER = {'Connection': 'keep-alive', 'User-Agent': BROWSER}
AK = '9371554e0322b1941224d4ee36b2e366'
MEASUREMENT = 'duration'


class AMapAPI:
    def getAPIDist(self, destination, origins):
        global AK
        url = 'http://restapi.amap.com/v3/distance?key={}&origins={}&destination={}'.format(AK, origins, destination)
        jsonDist = json.loads(self.queryJson(url))
        return jsonDist

    @retry
    def queryJson(self, url):
        while True:
            try:
                result = requests.get(url, headers=HEADER).text
            except (socket.timeout, requests.exceptions.Timeout):  # socket.timeout
                raise Exception('timeout',url)
            except requests.exceptions.ConnectionError:
                raise Exception('connection error',url)
            else:
                try:
                    json.loads(result)
                except ValueError:
                    print "no json return, retry."
                except:
                    print "unknown error, retry."
                else:
                    break
        return result

    def JSDecode(self, dic):
        if dic['info'] == "OK" and dic['status'] == "1":
            res = dic['results']
            return res
        else:
            print ("连接信息出错")
            return

    def getTimeDistVec(self, destination, originVec,orderNum):
        distVec = np.zeros([orderNum], dtype=int)
        # 排除调取接口的时间（临时处理）
        # batchNum = 50
        # destStr = '%lf' % destination[1] + ',' + '%lf' % destination[0]
        # if orderNum == 1:
        #     originStr = '%lf' % originVec[1] + ',' + '%lf' % originVec[0]
        #     JSDistance = self.getAPIDist(originStr, destStr)
        #     result = self.JSDecode(JSDistance)
        #     distVec[0] = result[0][MEASUREMENT]
        # else:
        #     if orderNum % batchNum == 0:
        #         xxrange = orderNum/batchNum
        #     else:
        #         xxrange = orderNum/batchNum + 1
        #
        #     for i in xrange(xxrange):
        #         tmpOriginStr = ''
        #         for j in xrange(i * batchNum, min((i + 1) * batchNum, orderNum)):
        #             tmpOriginStr = tmpOriginStr + '%lf' % originVec[j][1] + ',' + '%lf' % originVec[j][0] + '|'
        #         originStr = tmpOriginStr[0:-1]
        #         JSDistance = self.getAPIDist(destStr, originStr)
        #         result = self.JSDecode(JSDistance)
        #         for j in xrange(len(result)): distVec[(i * batchNum) + j] = result[j][MEASUREMENT]
        return distVec