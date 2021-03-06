import requests

base_url = 'https://v5.db.transport.rest/'


def station(name):
    query_params = {'query': name, 'results': 1}
    response = requests.get(base_url + 'locations', params=query_params).json()
    return response[0]['id']


def journeys(start_id, destination_id, max_journeys=3):
    query_params = {'from': start_id, 'to': destination_id}
    response = requests.get(base_url + 'journeys', params=query_params).json()['journeys']
    return response[:min(max_journeys, len(response))]


def board_information(all_journeys):
    board = dict()
    board['trains'] = list()
    for leg in [journey['legs'][0] for journey in all_journeys]:
        board['start'] = leg['origin']['name']
        if leg['departure']:
            train = dict()
            train['planned_departure'] = leg['plannedDeparture']
            if leg['departureDelay']:
                train['delay'] = str(int(leg['departureDelay'])//60)
            else:
                train['delay'] = '0'
            train['platform'] = leg['departurePlatform']
            train['train'] = leg['line']['name']
            board['trains'].append(train)

    # Get correct destination
    legs = all_journeys[0]['legs']
    board['destination'] = legs[len(legs)-1]['destination']['name']

    return board


def connections(start_name, destination_name):
    start_id = station(start_name)
    destination_id = station(destination_name)
    return board_information(journeys(start_id, destination_id))
