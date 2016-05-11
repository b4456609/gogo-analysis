"""SimpleApp"""

from pyspark import SparkContext
import WeatherClient
import math
import datetime
sc = SparkContext("local","Weather Analyzer",pyFiles=['WeatherClient.py', 'WeatherServiceClient.py', 'Model.py'])

metrics = WeatherClient.basic_metrics()
# metrics.uv = WeatherClient.getUV()

sun = WeatherClient.getSunTime()
metrics.sunrise = sun['sunrise']
metrics.sunset = sun['sunset']
print sun

def weather(x):
    return 0.6 * x.temp + 0.4 * x.humd

def uv(x):
    res = x.uv * -100 / 11 + 100
    # return -1 if is not valid
    if res > 100 or res < 0:
        return -1
    return res

def time(x):
    mins = x.time.hour * 60 + x.time.minute
    res = 0.5 * math.cos((mins-720) * 2 * math.pi / 1440) + 0.5
    res *= 100

    sunrise_delta = mins - x.sunrise.hour * 60 - x.sunrise.minute
    sunset_delta = mins - x.sunset.hour * 60 - x.sunset.minute
    if sunrise_delta < 0:
        res -= 5
    elif

    # return -1 if is not valid
    if res > 100 or res < 0:
        return -1
    return int(res)

metrics = sc.parallelize([metrics])
# weatherValue = metrics.map(weather).first()
# uvValue = metrics.map(uv).first()
timeValue = metrics.map(time).first()
print timeValue