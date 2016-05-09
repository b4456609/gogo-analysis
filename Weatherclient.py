import requests
import xml.etree.ElementTree as ET


station_id = '466940'
# for keelung predict
geocode = '1001701'


def getapi(dataid):
    url = "http://opendata.cwb.gov.tw/opendataapi"

    querystring = {"dataid": dataid,
                   "authorizationkey": "CWB-4511DE0E-A96A-4A98-9A34-5535D92A0DBF"}

    headers = {
        'cache-control': "no-cache"
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    return(response)


def keelung_predict():
    response = getapi("F-D0047-049")
    root = ET.fromstring(response.text.encode('utf-8'))
    # for name space
    ns = {'cwb': 'urn:cwb:gov:tw:cwbcommon:0.1'}
    # xpath use geocode for keelung
    # path = ".//cwb:location[cwb:geocode='"+ geocode +"']"
    path = ".//cwb:location"
    location = root.findall(path, ns)

    for ele in location:
        if ele.find('cwb:geocode', ns).text.strip() == '1001701':
            # find target keelung location
            location = ele
            break

    print location
    description = location.findall("./cwb:weatherElement[cwb:elementName='WeatherDescription']/cwb:time/cwb:startTime", ns)
    print description
    for i in description:
        print i.text

def basic_metrics():
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

    print time, temp, humd, wind_speed_10min, wind_dir_10min


def rain_detial():
    response = getapi("O-A0002-001")
    root = ET.fromstring(response.text.encode('utf-8'))

    # for name space
    ns = {'cwb': 'urn:cwb:gov:tw:cwbcommon:0.1'}
    # xpath use station id
    path = "cwb:location[cwb:stationId='" + station_id + "']"

    location = root.find(path, ns)
    print location

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

    print time, rain_60min, rain_10min, rain_3hr, rain_6hr, rain_12hr, rain_24hr
rain_detial()