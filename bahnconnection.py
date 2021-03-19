import requests

base_url = 'https://v5.db.transport.rest/'


def station(name):
    query_params = {'query': name, 'results': 1}
    response = requests.get(base_url + 'locations', params=query_params).json()
    return response[0]['id']


def journeys(start_id, destination_id):
    query_params = {'from': start_id, 'to': destination_id}
    response = requests.get(base_url + 'journeys', params=query_params).json()['journeys']

    return response


def board_information(all_journeys):
    board = dict()
    board['trains'] = list()
    for leg in [journey['legs'][0] for journey in all_journeys]:
        board['start'] = leg['origin']['name']
        board['destination'] = leg['destination']['name']
        if leg['departure']:
            train = dict()
            train['planned_departure'] = leg['plannedDeparture']
            train['delay'] = leg['departureDelay']
            train['platform'] = leg['departurePlatform']
            train['train'] = leg['line']['name']
            board['trains'].append(train)
    return board


def connections(start_name, destination_name):
    start_id = station(start_name)
    destination_id = station(destination_name)
    return board_information(journeys(start_id, destination_id))
