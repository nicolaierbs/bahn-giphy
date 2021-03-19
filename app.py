import slackbot
import fbbot
from flask import Flask, request, make_response

app = Flask(__name__)


@app.route('/', methods=['GET'])
def facebook_verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if fbbot.verify_webhook(request.args.get("hub.verify_token")):
            return request.args["hub.challenge"], 200
        else:
            return "Verification token mismatch", 403

    return "Hello world", 200


@app.route('/', methods=['POST'])
def facebook_webhook():
    # endpoint for processing incoming messaging events
    fbbot.message_webhook(request.get_json())
    return "ok", 200


@app.route("/slack/commands", methods=["POST"])
def slack_webhook():
    if slackbot.webhook(request.form):
        return make_response("", 200)
    else:
        return make_response("", 404)


if __name__ == '__main__':
    app.run(debug=True)
