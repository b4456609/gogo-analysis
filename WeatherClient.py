# -*- coding: UTF-8 -*-

import requests
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from xml.dom.minidom import Node
import datetime
from Model import Metrics
import dateutil.parser
import collections

station_id = '466940'
# for keelung predict
geocode = '1001701'

# for sunset and sunrise
lat = '25.1276033'
lng = '121.7391833'

uv_site = '基隆'

SunTime = collections.namedtuple('SunTime',
                                    ['sunrise','sunset'])
def getSunTime():
    url = 'http://api.sunrise-sunset.org/json?lat=' + lat + '&lng=' + lng + '&formatted=0'
    response = requests.get(url)
    data = json.loads(response.content)
    sunrise = dateutil.parser.parse(data['results']['sunrise']) + datetime.timedelta(hours=8)
    sunset = dateutil.parser.parse(data['results']['sunset']) + datetime.timedelta(hours=8)
    return SunTime(sunrise=sunrise.time(), sunset=sunset.time())


def getUV():
    url = "http://opendata.epa.gov.tw/ws/Data/UV/"

    querystring = {"$orderby": "PublishAgency",
                   "$skip": "0", "$top": "1000", "format": "json"}

    headers = {
        'cache-control': "no-cache"
    }
    try:
        response = requests.request(
            "GET", url, headers=headers, params=querystring)
        j = json.loads(response.text.encode('utf-8').decode('utf-8'))
        for i in j:
            if i['SiteName'].encode('utf-8') == uv_site:
                if float(i['UVI']) >= 0:
                    return float(i['UVI'])
                else:
                    return None
    except Exception as e:
        print "Unexpected error in getUV"
        print str(e)
        return None


def remove_blanks(node):
    for x in node.childNodes:
        if x.nodeType == Node.TEXT_NODE:
            if x.nodeValue:
                x.nodeValue = x.nodeValue.strip()
        elif x.nodeType == Node.ELEMENT_NODE:
            remove_blanks(x)


def getapi(dataid):
    url = "http://opendata.cwb.gov.tw/opendataapi"

    querystring = {"dataid": dataid,
                   "authorizationkey": "CWB-4511DE0E-A96A-4A98-9A34-5535D92A0DBF"}

    headers = {
        'cache-control': "no-cache"
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    return (response)


def keelung_predict():
    response = getapi("F-D0047-049")
    response_xml = minidom.parseString(response.text.encode('utf-8'))
    remove_blanks(response_xml)
    response_xml.normalize()
    root = ET.fromstring(response_xml.toxml('utf-8'))
    # for name space
    ns = {'cwb': 'urn:cwb:gov:tw:cwbcommon:0.1'}
    # xpath use geocode for keelung
    path = ".//cwb:location[cwb:geocode='" + geocode + "']"
    # path = ".//cwb:geocode"
    location = root.find(path, ns)

    temp = location.findall(
        "./cwb:weatherElement[cwb:elementName='T']//cwb:value", ns)
    humid = location.findall(
        "./cwb:weatherElement[cwb:elementName='RH']//cwb:value", ns)
    predictRate = location.findall(
        "./cwb:weatherElement[cwb:elementName='PoP']//cwb:value", ns)
    des = location.findall(
        "./cwb:weatherElement[cwb:elementName='WeatherDescription']//cwb:value", ns)


BasicMetrics = collections.namedtuple('BasicMetrics',
                                    ['time', 'temp', 'humd', 'wind_speed_10min', 'wind_dir_10min'])

def basic_metrics():
    response = getapi("O-A0003-001")
    root = ET.fromstring(response.text.encode('utf-8'))

    # for name space
    ns = {'cwb': 'urn:cwb:gov:tw:cwbcommon:0.1'}
    # xpath use station id
    path = "cwb:location[cwb:stationId='" + station_id + "']"

    try:
        location = root.find(path, ns)

        time = location.find(".//cwb:obsTime", ns).text
        temp = location.find(
            "./cwb:weatherElement[cwb:elementName='TEMP']/cwb:elementValue/cwb:value", ns).text
        humd = location.find(
            "./cwb:weatherElement[cwb:elementName='HUMD']/cwb:elementValue/cwb:value", ns).text
        wind_speed_10min = location.find(
            "./cwb:weatherElement[cwb:elementName='H_F10']/cwb:elementValue/cwb:value", ns).text
        wind_dir_10min = location.find(
            "./cwb:weatherElement[cwb:elementName='H_10D']/cwb:elementValue/cwb:value", ns).text

        time = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S+08:00")
        humd = float(humd)
        temp = float(temp)
        wind_speed_10min = float(wind_speed_10min)
        wind_dir_10min = float(wind_dir_10min)

        return BasicMetrics(time=time,temp=temp,humd=humd,wind_speed_10min=wind_speed_10min,wind_dir_10min=wind_dir_10min)
    except Exception as e:
        print "Unexpected error in basic_metrics"
        print str(e)
        return None


RainDetail = collections.namedtuple('RainDetail',
                                    ['time', 'rain_10min', 'rain_60min', 'rain_3hr', 'rain_6hr', 'rain_12hr',
                                     'rain_24hr'])


def rain_detial():
    response = getapi("O-A0002-001")
    root = ET.fromstring(response.text.encode('utf-8'))

    # for name space
    ns = {'cwb': 'urn:cwb:gov:tw:cwbcommon:0.1'}
    # xpath use station id
    path = "cwb:location[cwb:stationId='" + station_id + "']"

    try:
        location = root.find(path, ns)
        if location == None:
            return None

        time = location.find(".//cwb:obsTime", ns).text
        rain_60min = location.find(
            "./cwb:weatherElement[cwb:elementName='RAIN']/cwb:elementValue/cwb:value", ns).text
        rain_10min = location.find(
            "./cwb:weatherElement[cwb:elementName='MIN_10']/cwb:elementValue/cwb:value", ns).text
        rain_3hr = location.find(
            "./cwb:weatherElement[cwb:elementName='HOUR_3']/cwb:elementValue/cwb:value", ns).text
        rain_6hr = location.find(
            "./cwb:weatherElement[cwb:elementName='HOUR_6']/cwb:elementValue/cwb:value", ns).text
        rain_12hr = location.find(
            "./cwb:weatherElement[cwb:elementName='HOUR_12']/cwb:elementValue/cwb:value", ns).text
        rain_24hr = location.find(
            "./cwb:weatherElement[cwb:elementName='HOUR_24']/cwb:elementValue/cwb:value", ns).text

        return RainDetail(time=time, rain_3hr=rain_3hr, rain_6hr=rain_6hr, rain_10min=rain_10min, rain_12hr=rain_12hr,
                          rain_24hr=rain_24hr, rain_60min=rain_60min)
    except Exception as e:
        print "Unexpected error in rain_detial"
        print str(e)
        return None


AirPollution = collections.namedtuple('AirPollution', ['psi', 'pm2_5'])

def air_pollution():
    try:
        url = "http://opendata2.epa.gov.tw/AQX.json"

        headers = {
            'cache-control': "no-cache",
        }

        response = requests.request("GET", url, headers=headers)

        data = json.loads(response.content)
        for i in data:
            if i['County'].encode('utf-8') == '基隆市':
                psi = int(i['PSI'])
                pm2_5 = int(i['PM2.5'])
                return AirPollution(psi=psi, pm2_5=pm2_5)
    except Exception as e:
        print "Unexpected error in rain_detial"
        print str(e)
        return None
