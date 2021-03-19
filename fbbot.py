import requests
from requests_toolbelt import MultipartEncoder
import os
import sys
from datetime import datetime
import json
import bahnconnection
import gifted

api_version = 2.6
graph_url = 'https://graph.facebook.com/v{0}'.format(api_version)


def verify_webhook(verify_token):
    log('Challenge token')
    return verify_token == os.environ["VERIFY_TOKEN"]


def message_webhook(data):
    log(data)  # you may not want to log every incoming message in production, but it's good for testing
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"][
                        "id"]  # the recipient's ID, which should be your page's facebook ID
                    if "text" in messaging_event["message"]:
                        message_text = messaging_event["message"]["text"]  # the message's text
                        log("sending message from {sender} to {recipient}: {text}"
                            .format(recipient=recipient_id, sender=sender_id, text=message_text))

                        try:
                            stations = message_text.split(' nach ')
                            if len(stations) == 2:
                                connections = bahnconnection.connections(stations[0], stations[1])
                                log('Found connections: {}'.format(str(connections)))
                                connections = bahnconnection.connections('Darmstadt', 'Frankfurt')
                                img_path = gifted.create(
                                    scene='landscape-summer',
                                    train='bahn_angela',
                                    num_frames=50,
                                    connections=connections,
                                    text='#dbregiodatahack21')
                                log('Created gif')
                                img = open(img_path, mode='rb').read()
                                send_attachment(sender_id, 'image', img)
                            else:
                                log('Send tutorial message')
                                send_message(sender_id,
                                             'Bitte gebe deine Anfrage in dem Muster "Bahnhof nach Bahnhof" ein.')
                        except KeyError:
                            send_message(sender_id, 'Leider ist ein Fehler im System aufgetreten.')
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass


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
    r = requests.post('{}/me/messages'.format(graph_url), params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
    return r


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


def send_attachment(recipient_id, attachment_type, image_data):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        'recipient': json.dumps({
            'id': recipient_id
        }),
        # 'notification_type': notification_type.value,
        'message': json.dumps({
            'attachment': {
                'type': attachment_type,
                'payload': {}
            }
        }),
        'filedata':
            ('Deine Verbindung', image_data, 'image/gif')
    }
    multipart_data = MultipartEncoder(data)
    multipart_headers = {'Content-Type': multipart_data.content_type}
    log('Start sending...')
    r = requests.post('{}/me/messages'.format(graph_url), params=params, data=multipart_data, headers=multipart_headers)
    log('Sent')
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
    return r
