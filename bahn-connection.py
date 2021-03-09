import configparser
import requests
from datetime import datetime, timedelta
import urllib.parse

config_section = 'BAHN'
params = configparser.ConfigParser()
params.read('parameters.ini')

url = params.get(config_section, 'schema') + params.get(config_section, 'host') + params.get(config_section, 'base_path')
token = params.get(config_section, 'token')

headers = {'Authorization': 'Bearer ' + token}

date_format = '%Y-%m-%dT%H:%M'


def station(name):
    r = requests.get(url + '/location/' + name, headers=headers).json()
    return r[0]['id']


def leaving_trains(station_id, minutes=None):
    request_params = {'date': datetime.today().strftime(date_format) }
    trains = requests.get(url + '/departureBoard/' + str(station_id), params=request_params, headers=headers).json()

    # Filter trains only in the near future
    if minutes:
        latest_time = datetime.now() + timedelta(minutes=minutes)
        trains = [x for x in trains if datetime.strptime(x['dateTime'], date_format) < latest_time]

    return trains


def filter_trains(all_trains, start_station_id, end_station_id):
    selected_trains = list()
    for train in all_trains:
        # print(train['detailsId'])
        path = urllib.parse.quote('/journeyDetails/' + train['detailsId'])
        # print(path)
        stops = requests.get(url + path, headers=headers).json()

        # Train should first pass through start and then through end
        if valid_train(stops, start_station_id, end_station_id):
            start_stop = [stop for stop in stops if stop['stopId'] == start_station_id]
            train['depTime'] = start_stop[0]['depTime']
            selected_trains.append(train)
    return selected_trains


def valid_train(stops, start_station_id, end_station_id):
    # Is train passing through end station?
    if not any(stop['stopId'] == end_station_id for stop in stops):
        return False

    # Is train passing first through start and then through end station?
    for stop in stops:
        if stop['stopId'] == start_station_id:
            return True
        elif stop['stopId'] == end_station_id:
            return False

    return False


start = station('Darmstadt')
end = station('Frankfurt Main')
good_trains = leaving_trains(start, 3600)
print(good_trains)
relevant_trains = filter_trains(good_trains, start, end)
print(relevant_trains)
