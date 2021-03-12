
from slack_sdk.webhook import WebhookClient
from flask import Flask, request, make_response


app = Flask(__name__)


@app.route("/slack/events", methods=["POST"])
def slack_app():
    # Handle a slash command invocation
    if "command" in request.form \
            and request.form["command"] == "/reply-this":
        response_url = request.form["response_url"]
        text = request.form["text"]
        webhook = WebhookClient(response_url)
        # Send a reply in the channel
        response = webhook.send(text=f"You said '{text}'")
        # Acknowledge this request
        return make_response("", 200)

    return make_response("", 404)
