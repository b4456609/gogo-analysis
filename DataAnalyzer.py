"""SimpleApp"""

from pyspark import SparkContext
import WeatherClient
import math
import json
import WeatherServiceClient
import time


def weather(x):
    tempValue = -4 / 9.0 * x.temp ** 2 + 200 / 9.0 * x.temp - 1600 / 9.0
    humd = round(x.humd * 100)
    if humd < 40:
        humdValue = humd * 100 / 40
    elif humd > 50:
        humdValue = -2 * humd + 200
    else:
        humdValue = 100
    print humd, tempValue
    res = 0.6 * tempValue + 0.4 * humdValue
    if res < 0 or res > 100:
        return -1
    return int(res)


def uv(x):
    res = x * -100 / 11.0 + 100
    # return -1 if is not valid
    if res > 100 or res < 0:
        return -1
    return int(res)


def timeCal(x):
    # minutes today
    mins = x['basicMetrics'].time.hour * 60 + x['basicMetrics'].time.minute
    res = 0.5 * math.cos((mins - 720) * 2 * math.pi / 1440.0) + 0.5
    res *= 100

    # time to sunrise delta
    sunrise_delta = mins - x['sun'].sunrise.hour * 60 - x['sun'].sunrise.minute
    # time to sunset delta
    sunset_delta = mins - x['sun'].sunset.hour * 60 - x['sun'].sunset.minute
    if sunrise_delta < 0:
        res -= 5
    elif sunset_delta > 0:
        res += 5

    # return -1 if is not valid
    if res > 100:
        return 100
    if res < 0:
        return 0
    return int(res)


def rainCal(x):
    if x <= 0.0:
        return 100
    elif x <= 3.0:
        return -40 / 3.0 * x + 100
    elif x > 15.0:
        return 0
    elif x > 3.0:
        return -5 * x + 75
    else:
        return -1


def airCal(x):
    res = 0.5 * (100.0 - x.psi / 3.0) + 0.5 * (100.0 - x.pm2_5 * 100.0 / 71.0)
    return int(res)


def request():
    # request for metrics
    basicMetrics = WeatherClient.basic_metrics()
    uvMetrics = WeatherClient.getUV()
    sun = WeatherClient.getSunTime()
    rainMetrics = WeatherClient.rain_detial()
    airMetrics = WeatherClient.air_pollution()
    # predictMetrics = WeatherClient.keelung_predict()
    LOGGER.info('basicMetrics' + basicMetrics.__str__())

    print basicMetrics
    print uvMetrics
    print sun
    print rainMetrics
    print airMetrics

    jsonBody = {
        'basic': None,
        'uv': None,
        'sun': None,
        'rain': None,
        'air': None,
        'value': {
            'weather': None,
            'uv': None,
            'sun': None,
            'rain': None,
            'air': None
        }
    }

    if basicMetrics is not None:
        weather_value = sc.parallelize([basicMetrics]).map(weather).first()
        jsonBody['value']['weather'] = weather_value
        LOGGER.info('weatherValue' + str(weather_value))

    if uvMetrics is not None:
        uvValue = sc.parallelize([uvMetrics]).map(uv).first()
        jsonBody['value']['uv'] = uvValue
        LOGGER.info('uvValue' + str(uvValue))
        jsonBody['uv'] = uvMetrics

    if sun is not None and basicMetrics is not None:
        timeValue = sc.parallelize([{'basicMetrics': basicMetrics, 'sun': sun}]).map(timeCal).first()
        jsonBody['value']['sun'] = timeValue
        LOGGER.info('timeValue' + str(timeValue))
        sun.sunrise = sun.sunrise.isoformat()
        sun.sunset = sun.sunset.isoformat()
        jsonBody['sun'] = sun.__dict__

    if rainMetrics is not None:
        rainValue = sc.parallelize([rainMetrics.rain_10min]).map(rainCal).first()
        jsonBody['value']['rain'] = rainValue
        jsonBody['rain'] = rainMetrics.__dict__

    if airMetrics is not None:
        airValue = sc.parallelize([airMetrics]).map(airCal).first()
        jsonBody['value']['air'] = airValue
        LOGGER.info('airValue' + str(airValue))
        jsonBody['air'] = airMetrics.__dict__

    basicMetrics.time = basicMetrics.time.isoformat()
    jsonBody['basic'] = basicMetrics.__dict__

    return jsonBody


def main():
    while True:
        jsonBody = request()
        print json.dumps(jsonBody)
        WeatherServiceClient.postWeather(json.dumps(jsonBody))
        time.sleep(180)


# sc = SparkContext("local", "Weather Analyzer", pyFiles=['WeatherClient.py', 'WeatherServiceClient.py'])
# sc = SparkContext("spark://bernie-All-Series:7077", "Weather Analyzer", pyFiles=['WeatherClient.py', 'WeatherServiceClient.py'])
# sc = SparkContext("spark://140.121.101.164:7077", "Weather Analyzer", pyFiles=['WeatherClient.py', 'WeatherServiceClient.py'])
sc = SparkContext("local", "Weather Analyzer", pyFiles=['WeatherClient.py', 'WeatherServiceClient.py'])

# get logger
log4jLogger = sc._jvm.org.apache.log4j
LOGGER = log4jLogger.LogManager.getLogger(__name__)
main()
