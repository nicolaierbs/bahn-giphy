import os
from slack_sdk import WebClient
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
import asyncio
from aiohttp import web
import bahnconnection
import gifted
import configparser


config_section = 'SLACK'
params = configparser.ConfigParser()
params.read('parameters.ini')

token = params.get(config_section, 'token')

client = WebClient(token=token)


def send_gif(file):
    try:
        response = client.files_upload(channels='#team_gif-ted', file=file)
        assert response["file"]  # the uploaded file
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")


scenes = ['landscape-winter']
# scenes = ['landscape-summer', 'landscape-winter']
trains = ['ice_comic']
# trains = ['bahn_angela', 'ice_comic', 'rb_vbb', 're_vbb', 'sbahn_vbb']

connections = bahnconnection.connections('Darmstadt', 'Frankfurt')

send_gif(gifted.create(scene='landscape-summer', train='bahn_angela', num_frames=50, connections=connections, text='#dbregiodatahack21'))
# send_gif(gifted.create(scene='landscape-winter', train='bahn_angela', num_frames=50, connections=connections, text='#dbregiodatahack21'))
# send_gif(gifted.create(scene='landscape-winter', train='ice_comic', num_frames=50, connections=connections, text='#dbregiodatahack21'))
# send_gif(gifted.create(scene='landscape-summer', train='re_vbb', num_frames=50, connections=connections, text='#dbregiodatahack21'))
