"""SimpleApp"""

from pyspark import SparkContext
import client

logFile = "/home/bernie/pf/spark-1.6.1-bin-hadoop2.6/README.md"
sc = SparkContext("local","Simple App")
logData = sc.textFile(logFile).cache()

numAs = logData.filter(lambda s: 'a' in s).count()
numBs = logData.filter(lambda s: 'b' in s).count()


print("Lines with a: %i, lines with b: %i"%(numAs, numBs))

client.rain_detial()