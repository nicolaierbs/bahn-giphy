import configparser
import requests

config_section = 'WEATHER'
params = configparser.ConfigParser()
params.read('parameters.ini')

api_key = params.get(config_section, 'key')
api_url = params.get(config_section, 'url')


def city(name):
    query_params = {'q': name, 'appid': api_key, 'units': 'metric', 'lang': 'de'}
    response = requests.get(api_url, params=query_params).json()
    return response


print(city('Darmstadt'))
