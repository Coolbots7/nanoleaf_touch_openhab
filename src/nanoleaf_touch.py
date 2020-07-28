# -*- coding: utf-8 -*-

import requests
import logging
import json
import sys

logging.basicConfig(filename='./nanoleafTouches.log',
                    level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.info("Started")

canvasIP = 'nanoleaf.cb7.com:16021'
canvasToken = 'I9noXwEG6b1UUbUy8qKuwGip7pWP9w9y'
canvasEvent = '/events?id=4'  # touch

openHabIp = 'openhab.cb7.com'
openhabGestureItem = '/rest/items/CanvasTouchGesture'
openhabIdItem = '/rest/items/CanvasTouchId'

canvasGetUrl = 'http://'+canvasIP+'/api/v1/'+canvasToken+canvasEvent
openHabPostUrlGesture = 'http://'+openHabIp+openhabGestureItem
openHabPostUrlId = 'http://'+openHabIp+openhabIdItem

headersGET = {'Accept': 'application/json',
              'Content-Type': 'application/json', }
headersPOST = {'Accept': 'application/json', 'Content-Type': 'text/plain', }

def connectToCanvas():
    global response
    global rr
    global newlineSeen

    response = requests.get(canvasGetUrl, headers=headersGET, stream=True)
    logging.info('Listening...')
    rr = ''
    newlineSeen = False


def parseEvent():
    global rr
    print("parse")
    rr = rr[12:]  # throw away no JSON part (is always id=4)
    logging.info(rr)
    loaded_json = json.loads(rr)
    gesture = loaded_json['events'][0]['gesture']
    panelId = loaded_json['events'][0]['panelId']
    print(gesture)
    print(panelId)
    res1 = requests.post(openHabPostUrlGesture,
                         headers=headersPOST, data=str(gesture))
    res2 = requests.post(
        openHabPostUrlId, headers=headersPOST, data=str(panelId))


def rxEvent():
    global response
    global rr
    global newlineSeen

    r = response.raw.read(1)  # parse every single byte received until /n/n
    if len(r) == 0:
        connectToCanvas()  # connection was lost, re-connect
    else:
        r = r.decode("utf-8")
        if newlineSeen:
            if r == '\n':
                parseEvent()
                newlineSeen = False
                rr = ''  # start over
            else:
                newlineSeen = False
                rr = rr+r  # accumulate
        else:
            if r == '\n':
                newlineSeen = True
                rr = rr+' '  # replace \n with ' '
            else:
                rr = rr+r  # accumulate


connectToCanvas()
while True:
    try:
        # typical response:
        # id: 4\ndata: {"events":[{"panelId":42794,"gesture":0}]}\n\n
        rxEvent()
    except KeyboardInterrupt:
        sys.exit("Program stopped using CTRL+C")

# never stop listening
