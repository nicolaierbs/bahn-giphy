import slackbot
import fbbot
from flask import Flask, request, make_response

app = Flask(__name__)


@app.route('/', methods=['GET'])
def facebook_verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    print('challenge from facebook')
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if fbbot.verify_webhook(request.args.get("hub.verify_token")):
            return request.args["hub.challenge"], 200
        else:
            return "Verification token mismatch", 403

    return "Hello world", 200


@app.route('/', methods=['POST'])
def facebook_webhook():
    # endpoint for processing incoming messaging events
    try:
        data = request.get_json()
        fbbot.message_webhook(data)
        return "ok", 200
    finally:
        return "server error", 500


@app.route("/slack/commands", methods=["POST"])
def slack_webhook():
    if slackbot.webhook(request.form):
        return make_response("", 200)
    else:
        return make_response("", 404)


if __name__ == '__main__':
    app.run(debug=True)
