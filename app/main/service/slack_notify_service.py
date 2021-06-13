import datetime
import os
from app.main import db
import pytz
from dotenv import load_dotenv
from slack_sdk.webhook import WebhookClient
from app.main.model import Miner
load_dotenv()
slack_url = os.getenv("SLACK_WEB_HOOK_URL")
webhook = WebhookClient(slack_url)


def notify_slack(invalid_share):
    time = invalid_share.time
    gpu_no = invalid_share.gpu_no
    miner_id = invalid_share.miner_id
    miner = db.session.query(Miner) \
        .filter(Miner.id == miner_id)\
        .first()
    miner_name = miner.name
    miner_user = miner.user.username

    title = "Invalid share reported"

    text = f"***[{time}]*** {title} \n\t{miner_user} - {miner_name} : GPU {gpu_no}"

    blocks = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": text
        }
    }]

    # send the slack message
    response = webhook.send(
        text=title,
        blocks=blocks
    )

    assert response.status_code == 200, f"{response.status_code} received from Slack"
    assert response.body == "ok", f"{response.body} received from Slack"
