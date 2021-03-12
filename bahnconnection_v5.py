import configparser
import requests
from datetime import datetime

config_section = 'V5'
params = configparser.ConfigParser()
params.read('parameters.ini')

base_url = params.get(config_section, 'schema') + params.get(config_section, 'host')


def station(name):
    query_params = {'query': name, 'results': 1}
    response = requests.get(base_url + 'locations', params=query_params).json()
    return response[0]['id']


def journeys(start_id, destination_id):
    query_params = {'from': start_id, 'to': destination_id}
    response = requests.get(base_url + 'journeys', params=query_params).json()['journeys']

    return response


def clean_leg(leg):
    if not leg['departure']:
        return None
    journey = dict()
    journey['start'] = leg['origin']['name']
    journey['destination'] = leg['destination']['name']
    journey['departure'] = leg['departure']
    journey['planned_departure'] = leg['plannedDeparture']
    journey['delay'] = leg['departureDelay']
    journey['platform'] = leg['departurePlatform']
    journey['train'] = leg['line']['name']
    return journey


def connections(start_name, destination_name):
    start_id = station(start_name)
    destination_id = station(destination_name)
    filtered_journeys = [clean_leg(journey['legs'][0]) for journey in journeys(start_id, destination_id)]
    return [filtered_journey for filtered_journey in filtered_journeys if filtered_journey]
