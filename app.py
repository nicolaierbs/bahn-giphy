
from slack_sdk.webhook.client import WebhookClient
from flask import Flask, request, make_response


app = Flask(__name__)


@app.route("/slack/commands", methods=["POST"])
def slack_app():
    print(request.form)
    # Handle a slash command invocation
    if "command" in request.form \
            and request.form["command"] == "/gif-ted":
        response_url = request.form["response_url"]
        text = request.form["text"]
        webhook = WebhookClient(response_url)
        # Send a reply in the channel
        response = webhook.send(text=f"You said '{text}'")
        # Acknowledge this request
        return make_response("", 200)

    return make_response("", 404)


@app.route("/", methods=["GET"])
def hello():
    # Acknowledge this request
    return make_response("Hello world!", 200)
