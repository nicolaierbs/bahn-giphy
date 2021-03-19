import requests
import os


api_key = os.environ["WEATHER_API_KEY"]
api_url = os.environ["WEATHER_API_URL"]


def city(name):
    query_params = {'q': name, 'appid': api_key, 'units': 'metric', 'lang': 'de'}
    response = requests.get(api_url, params=query_params).json()
    return response
