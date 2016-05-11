import requests
import json

def postWeather(obj):
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache",
        'postman-token': "e5f03c44-02e7-32f7-4997-d9e001f44d65"
        }

    url = "http://140.121.101.163:7084/user/sync"

    payload = obj.__dict__

    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)