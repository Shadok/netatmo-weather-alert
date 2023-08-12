#!/usr/bin/python
# -*- coding: utf-8 -*-

import lnetatmo
import requests
import json
import sys
import time
from datetime import datetime

# Mail
import smtplib
import os

def sendMail( subject, content ):
    """ Send a simple, stupid, text, UTF-8 mail in Python """

    for ill in [ "\n", "\r" ]:
        subject = subject.replace(ill, ' ')

    headers = {
        'Content-Type': 'text/html; charset=utf-8',
        'Content-Disposition': 'inline',
        'Content-Transfer-Encoding': '8bit',
        'From': '', # To fill
        'To': '', # To fill
        'Date': datetime.now().strftime('%a, %d %b %Y  %H:%M:%S %Z'),
        'X-Mailer': 'python',
        'Subject': subject
    }

    # create the message
    msg = ''
    for key, value in headers.items():
        msg += "%s: %s\n" % (key, value)

    # add contents
    msg += "\n%s\n"  % (content)

    s = smtplib.SMTP("localhost")

    s.sendmail(headers['From'], headers['To'], msg.encode("utf8"))
    s.quit()

authorization = lnetatmo.ClientAuth()
weather = lnetatmo.WeatherStationData(authorization)

user = weather.user
station_id="# To fill" # To fill

for station in weather.rawData :
    if station['_id'] == station_id :
        if not station['reachable']:
            sendMail( "[Netatmo] Station " + station['home_name'] + " injoignable !", "Injoignable depuis " + datetime.utcfromtimestamp( station['last_status_store'] ).strftime('%d-%m-%Y %H:%M:%S') + " UTC." )
        for module in station['modules'] :
            if not module['reachable'] :
                sendMail( "[Netatmo] Module " + module['module_name'] + " injoignable !", "Injoignable depuis " + datetime.utcfromtimestamp( module['last_message'] ).strftime('%d-%m-%Y %H:%M:%S') + " UTC. Sa batterie etait a " + str( module['battery_percent'] ) + " %." )
            elif module['battery_percent'] < 10 :
                sendMail( "[Netatmo] Remplacer les piles du module " + module['module_name'], "Sa batterie est a " + str( module['battery_percent'] ) + " % !" )
sys.exit()