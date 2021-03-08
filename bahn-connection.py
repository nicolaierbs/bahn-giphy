import configparser
import requests

config_section = 'BAHN'
params = configparser.ConfigParser()
params.read('parameters.ini')

url = params.get(config_section, 'schema') + params.get(config_section, 'host') + params.get(config_section, 'base_path')
print(url)
token = params.get(config_section, 'token')

headers = {'Authorization': 'Bearer ' + token}
r = requests.get(url + '/location/darmstadt', headers=headers)
response = r.json()
print(response)
