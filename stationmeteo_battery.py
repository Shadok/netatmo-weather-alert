#!/usr/bin/python
# -*- coding: utf-8 -*-
# Nom du Script:
# stationmeteo_battery.py
#
# Description du script:
# Script qui recupere le pourcentage des batteries
# des modules de la station meteo Netatmo
#
# Version du Script:
# V 1.0 du 30/01/2017
#
# Auteur original du script:
# Seb iDomo 
#

import requests
import json
#from lxml import etree
#from pprint import pprint
import sys
from datetime import datetime
import time

# Mail
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import formatdate
import os

def sendMail(subject, text):
    msg = MIMEMultipart()
    msg['From'] = "" # To fill
    msg['To'] = "" # To fill
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    smtp = smtplib.SMTP( "localhost" )
    smtp.sendmail(msg['From'], msg['To'], msg.as_string() )
    smtp.close()

# Debut du code fourni par Netatmo
payload = {'grant_type': 'password',
           'username': "", # To fill
           'password': "", # To fill
           'client_id':"", # To fill
           'client_secret': "", # To fill
           'scope': 'read_station'}
try:
    response = requests.post("https://api.netatmo.com/oauth2/token", data=payload)
    response.raise_for_status()
    access_token=response.json()["access_token"]
    scope=response.json()["scope"]
except requests.exceptions.HTTPError as error:
    print(error.response.status_code, error.response.text)

params = {
    'access_token': access_token,
    'device_id': '<station mac address>' # To fill
}

batteries = {}

try:
    response = requests.post("https://api.netatmo.com/api/getstationsdata", params = params)
    response.raise_for_status()
    data = response.json()["body"]
# Fin du code fourni par Netatmo
################################

    # Si la station est injoignable
    ts = time.time()
    ts_station = data[u'devices'][0][u'dashboard_data'][u'time_utc']
    if (ts - ts_station) > 60*30:
        sendMail("[Netatmo] Station non joignable","Inacessible depuis " + datetime.utcfromtimestamp(ts_station).strftime('%d-%m-%Y %H:%M:%S') + " UTC !")

# Recuperation du pourcentage restant de la batterie des differents modules de la station
    for mod in data[u'devices'][0][u'modules']:
		assert(u'battery_percent' in mod)
		percent = mod[u'battery_percent']
		mod_name = mod[u'module_name'].encode('utf-8')
		batteries[mod_name] = percent
                if not mod[u'reachable']:
                    sendMail("[Netatmo] Station " + mod_name + " injoignable !","Injoignable depuis " + datetime.utcfromtimestamp(mod[u'last_message']).strftime('%d-%m-%Y %H:%M:%S') + " UTC. Sa batterie etait a " + str( batteries[mod_name] ) + "%.")
		elif batteries[mod_name] < 15:
                    sendMail("[Netatmo] Remplacer les piles de la station " + mod_name,"Sa batterie est a " + str( batteries[mod_name] ) + "% !")

except requests.exceptions.HTTPError as error:
    print(error.response.status_code, error.response.text)

# Creation de la structure XML 
#ext = etree.Element("Ext")
#battery = etree.SubElement(ext, "Battery")

#for mod_name in batteries:
#	value = etree.SubElement(battery, mod_name)
#	value.text = str(batteries[mod_name])

#fichier = etree.ElementTree(ext)
#fichier.write("stationmeteo_battery.xml")

sys.exit()
