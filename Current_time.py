import os
import requests
import json


def get_current_time():

    url = "http://worldtimeapi.org/api/timezone/Africa/Lagos"
    api_response = requests.get(url)
    print(api_response.text)
    return json.dumps(api_response.text)

if __name__ == '__main__':
    get_current_time()
