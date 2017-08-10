# coding:utf-8
from flask import Flask, request
from sendtoairport import groupingdata
from recomTimeOnTheBus import recommendtime
from recomTimeOnTheBus import eastandwestside
import json

app = Flask(__name__)


@app.route('/toairport', methods=['post'])
def toairport():
    # print request.data
    # print type(request.data)
    args = json.loads(request.data)
    orderinfo = groupingdata.geteachTimepointSchedule(args)
    return orderinfo


@app.route('/provideordertime', methods=['post'])
def recomtime():
    args = request.data
    # print args
    # print "数据类型", type(args)
    jsonargs = json.loads(args)
    # print jsonargs
    re = recommendtime.RECOMDTIME()
    retime = re.getonthecardata(jsonargs)
    return retime


@app.route('/firstprovidetime', methods=['post'])
def firstprovidetime():
    args = request.data
    # print args
    # print "数据类型", type(args)
    jsonargs = json.loads(args)
    re = recommendtime.RECOMDTIME()
    retime = re.firstGetTime(jsonargs)
    return retime


@app.route('/inchengdu', methods=['post'])
def insidetwofive():
    args = request.data
    jsonargs = json.loads(args)
    si = eastandwestside.SIDE()
    side = si.orderinchengdutwofive(jsonargs)
    return side


if __name__ == '__main__':
    app.run('0.0.0.0')