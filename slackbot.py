import os
from slack_sdk import WebClient
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
import asyncio
from aiohttp import web
import bahnconnection
import gifted
import configparser
from slack_sdk.webhook.client import WebhookClient
import os


def send_gif(file):
    try:
        slack_client = WebClient(token=os.environ['SLACK_TOKEN'])
        response = slack_client = WebClient(token=os.environ['SLACK_TOKEN']).files_upload(channels='#team_gif-ted', file=file)
        assert response["file"]  # the uploaded file
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")


def webhook(form):
    print(form)
    # Handle a slash command invocation
    if "command" in form \
            and form['command'] == "/gif-ted":
        response_url = form['response_url']
        text = form['text']
        slack_webhook = WebhookClient(response_url)
        # Send a reply in the channel
        stations = text.split(' nach ')
        if len(stations) > 1:
            connections = bahnconnection.connections(stations[0], stations[1])
            # response = webhook.send(text=str(connections))
            text = 'Dein nächster Zug nach {destination} ist um {time} Uhr auf Bahnsteig {platform}. Gute Reise!'.format(
                platform=connections['trains'][0]['platform'],
                time=connections['trains'][0]['planned_departure'][11:16],
                destination=connections['destination'])
            slack_webhook.send(text=text)
        else:
            slack_webhook.send(text='Bitte gebe deine Anfrage in dem Muster "Bahnhof nach Bahnhof" ein.')
        return True
    return False
