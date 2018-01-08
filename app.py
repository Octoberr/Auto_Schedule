# coding: utf-8
from flask import Flask, request, Response
import json
import gevent.monkey
from gevent.pywsgi import WSGIServer
gevent.monkey.patch_all()

from sendtoairport import groupingdata
from sendtoairport import shortestpath
from recomTimeOnTheBus import recommendtime
from recomTimeOnTheBus import eastandwestside

app = Flask(__name__)


@app.route('/api/schedule/ClearPortSchedule', methods=['post'])
def clearPortSchedule():
    args = json.loads(request.data)
    orderinfo = groupingdata.geteachTimepointSchedule(args)
    return Response(orderinfo, mimetype="application/json")


@app.route('/api/schedule/SuggestPickupTime', methods=['post'])
def SuggestPickupTime():
    args = request.data
    # print args
    # print "数据类型", type(args)
    jsonargs = json.loads(args)
    re = recommendtime.RECOMDTIME()
    retime = re.firstGetTime(jsonargs)
    return Response(retime, mimetype="application/json")


@app.route('/api/schedule/ShortestPath', methods=['post'])
def SuggestShortestPath():
    args = request.data
    try:
        jsonargs = json.loads(args)
    except:
        return "no json data input,or inpudata error."
    try:
        triptype = jsonargs[0]['triptype']
    except:
        return "no triptype or trip type is wrong or no data"
    if triptype == 2:
        # 2为送机
        result = shortestpath.TheShortestPath(jsonargs)
        return Response(result, mimetype="application/json")
    elif triptype == 1:
        # 1为接机
        result = shortestpath.HomeShortestPath(jsonargs)
        return Response(result, mimetype="application/json")
    else:
        return "wrong trip type!"


# @app.route('/api/schedule/SuggestGroupPickupTime', methods=['post'])
# def SuggestGroupPickupTime():
#     args = request.data
#     # print args
#     # print "数据类型", type(args)
#     jsonargs = json.loads(args)
#     # print jsonargs
#     re = recommendtime.RECOMDTIME()
#     retime = re.getonthecardata(jsonargs)
#     return Response(retime, mimetype="application/json")


@app.route('/api/schedule/pinche', methods=['post'])
def insidetwofive():
    args = request.data
    jsonargs = json.loads(args)
    si = eastandwestside.SIDE()
    side = si.orderinchengdutwofive(jsonargs)
    return Response(side, mimetype="application/json")


@app.route('/api/schedule/zhuanche', methods=['post'])
def specifyinsidetwofive():
    args = request.data
    jsonargs = json.loads(args)
    si = eastandwestside.SIDE()
    side = si.specificitywholeChengDu(jsonargs)
    return Response(side, mimetype="application/json")


if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 8014), app)
    try:
        print("Start at " + http_server.server_host +
              ':' + str(http_server.server_port))
        http_server.serve_forever()
    except(KeyboardInterrupt):
        print('Exit...')