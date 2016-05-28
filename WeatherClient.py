# -*- coding: UTF-8 -*-

import requests
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from xml.dom.minidom import Node
import datetime
from  dateutil.parser import parse
import collections
import pytz

station_id = '466940'
# for keelung predict
geocode = '1001701'

# for sunset and sunrise
lat = '25.1276033'
lng = '121.7391833'

uv_site = '基隆'


class SunTime(object):
    def __init__(self, sunrise, sunset):
        self.sunrise = sunrise
        self.sunset = sunset

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


def getSunTime():
    try:
        url = 'http://api.sunrise-sunset.org/json?lat=' + lat + '&lng=' + lng + '&formatted=0'
        response = requests.get(url)
        data = json.loads(response.content)
        sunrise = parse(data['results']['sunrise']).astimezone(pytz.timezone('Asia/Taipei'))
        sunset = parse(data['results']['sunset']).astimezone(pytz.timezone('Asia/Taipei'))
        return SunTime(sunrise=sunrise, sunset=sunset)
    except Exception as e:
        print "Unexpected error in getUV"
        print str(e)
        return None


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
    try:
        url = "http://opendata.cwb.gov.tw/opendataapi"

        querystring = {"dataid": dataid,
                       "authorizationkey": "CWB-4511DE0E-A96A-4A98-9A34-5535D92A0DBF"}

        headers = {
            'cache-control': "no-cache"
        }

        response = requests.request(
            "GET", url, headers=headers, params=querystring)
        print response
        return response
    except Exception as e:
        print "Unexpected error in basic_metrics"
        print str(e)
        return None



def keelung_predict():
    try:
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
        time = location.findall(
            "./cwb:weatherElement[cwb:elementName='T']//cwb:dataTime", ns)
        temp = location.findall(
            "./cwb:weatherElement[cwb:elementName='T']//cwb:value", ns)
        humid = location.findall(
            "./cwb:weatherElement[cwb:elementName='RH']//cwb:value", ns)
        predictTime = location.findall(
            "./cwb:weatherElement[cwb:elementName='PoP']//cwb:startTime", ns)
        predictRate = location.findall(
            "./cwb:weatherElement[cwb:elementName='PoP']//cwb:value", ns)
            
        timevalue = []
        tempvalue = []
        humidvalue = []
        predictTimevalue = []
        predictRatevalue = []

        for i in time:
            timevalue.append(i.text)
        for i in temp:
            tempvalue.append(int(i.text) or 0)
        for i in humid:
            humidvalue.append(int(i.text) or 0)
        for i in predictTime:
            predictTimevalue.append(i.text)
        for i in predictRate:
            if i.text is not None:
                predictRatevalue.append(int(i.text) or 0)

        return {
            'time': timevalue,
            'temp': tempvalue,
            'humid': humidvalue,
            'predictTime': predictTimevalue,
            'predictRate': predictRatevalue
        }

    except Exception as e:
        print "Unexpected error in keelung_predict"
        print str(e)
        return None
keelung_predict()


class BasicMetrics(object):
    def __init__(self, time, temp, humd, wind_speed_10min, wind_dir_10min):
        self.time = time
        self.temp = temp
        self.humd = humd
        self.wind_speed_10min = wind_speed_10min
        self.wind_dir_10min = wind_dir_10min

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


def basic_metrics():
    try:
        response = getapi("O-A0003-001")
        root = ET.fromstring(response.text.encode('utf-8'))

        # for name space
        ns = {'cwb': 'urn:cwb:gov:tw:cwbcommon:0.1'}
        # xpath use station id
        path = "cwb:location[cwb:stationId='" + station_id + "']"

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

        time = parse(time)
        humd = max(float(humd), -1)
        temp = max(float(temp), -1)
        wind_speed_10min = max(float(wind_speed_10min), -1)
        wind_dir_10min = max(float(wind_dir_10min), -1)

        return BasicMetrics(time=time, temp=temp, humd=humd, wind_speed_10min=wind_speed_10min,
                            wind_dir_10min=wind_dir_10min)
    except Exception as e:
        print "Unexpected error in basic_metrics"
        print str(e)
        return None


RainDetail = collections.namedtuple('RainDetail',
                                    ['rain_10min', 'rain_60min', 'rain_3hr', 'rain_6hr', 'rain_12hr',
                                     'rain_24hr'])


def rain_detial():
    try:
        response = getapi("O-A0002-001")
        root = ET.fromstring(response.text.encode('utf-8'))

        # for name space
        ns = {'cwb': 'urn:cwb:gov:tw:cwbcommon:0.1'}
        # xpath use station id
        path = "cwb:location[cwb:stationId='" + station_id + "']"

        location = root.find(path, ns)
        if location == None:
            return None

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

        rain_3hr = max(float(rain_3hr),-1)
        rain_6hr = max(float(rain_6hr),-1)
        rain_10min = max(float(rain_10min),-1)
        rain_12hr = max(float(rain_12hr),-1)
        rain_24hr = max(float(rain_24hr),-1)
        rain_60min = max(float(rain_60min),-1)

        return RainDetail(rain_3hr=float(rain_3hr), rain_6hr=float(rain_6hr), rain_10min=float(rain_10min),
                          rain_12hr=float(rain_12hr),
                          rain_24hr=float(rain_24hr), rain_60min=float(rain_60min))
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
