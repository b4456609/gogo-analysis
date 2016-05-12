import requests
import json

def postWeather(obj):
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache",
        }

    url = "http://140.121.101.164:6000/weather"

    payload = json.dumps(obj)

    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)