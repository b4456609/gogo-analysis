import requests
import os

def postWeather(obj):
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache",
        }

    url = "http://140.121.101.164:5000/"

    payload = obj
    print payload
    response = requests.request("POST", url, data=payload, headers=headers)
    print  response