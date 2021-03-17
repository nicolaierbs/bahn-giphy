import os
import sys
import json
from datetime import datetime
import bahnconnection
from slack_sdk.webhook.client import WebhookClient

import requests
from flask import Flask, request, make_response

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    try:
                        stations = message_text.split(' nach ')
                        if len(stations) == 2:
                            connections = bahnconnection.connections(stations[0], stations[1])
                            text = 'Dein nächster Zug nach {destination} ist' \
                                   ' um {time} Uhr auf Bahnsteig {platform}. Gute Reise!'.format(
                                        platform=connections['trains'][0]['platform'],
                                        time=connections['trains'][0]['planned_departure'][11:16],
                                        destination=connections['destination'])
                            send_message(sender_id, text)
                        else:
                            send_message(sender_id, 'Bitte gebe deine Anfrage in dem Muster "Bahnhof nach Bahnhof" ein.')
                    except KeyError:
                        send_message(sender_id, 'Leider ist ein Fehler im System aufgetreten.')
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        else:
            msg = str(msg)
        print("{}: {}".format(datetime.now(), msg))
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()


@app.route("/slack/commands", methods=["POST"])
def slack_app():
    print(request.form)
    # Handle a slash command invocation
    if "command" in request.form \
            and request.form['command'] == "/gif-ted":
        response_url = request.form['response_url']
        text = request.form['text']
        slack_webhook = WebhookClient(response_url)
        # Send a reply in the channel
        stations = text.split(' nach ')
        if len(stations) > 1:
            connections = bahnconnection.connections(stations[0], stations[1])
            # response = slack_webhook.send(text=str(connections))
            text = 'Dein nächster Zug nach {destination} ist um {time} Uhr auf Bahnsteig {platform}. Gute Reise!'.format(
                platform=connections['trains'][0]['platform'],
                time=connections['trains'][0]['planned_departure'][11:16],
                destination=connections['destination'])
            response = slack_webhook.send(text=text)
        else:
            response = slack_webhook.send(text='Bitte gebe deine Anfrage in dem Muster "Bahnhof nach Bahnhof" ein.')
        # Acknowledge this request
        return make_response("", 200)

    return make_response("", 404)


if __name__ == '__main__':
    app.run(debug=True)
