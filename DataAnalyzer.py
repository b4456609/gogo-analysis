"""SimpleApp"""

from pyspark import SparkContext
import WeatherClient
sc = SparkContext("local","Weather Analyzer",pyFiles=['WeatherClient.py', 'WeatherServiceClient.py', 'Model.py'])

print sc.parallelize(WeatherClient.basic_metrics()).map(lambda x : x.cal()).first()