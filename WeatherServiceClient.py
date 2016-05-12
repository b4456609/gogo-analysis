import requests
import os

def postWeather(obj):
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache",
        }

    url = "http://" + os.environ.get('SERVICE_HOST') + "/weather"

    payload = obj

    response = requests.request("POST", url, data=payload, headers=headers)