from flask import Blueprint, render_template
from service.auth import current_user
import requests

from service.constants import STORIES_SERVICE_IP, STORIES_SERVICE_PORT


home = Blueprint('home', __name__)


def _strava_auth_url(config):
    return '127.0.0.1:5000'


@home.route('/')
def index():
    if current_user is not None and hasattr(current_user, 'id'):
        stories = get_story_by_author_id(current_user.id)
    else:
        stories = None
    return render_template("index.html", stories=stories, active_button="index")



def get_story_by_author_id(author_id):
    url = 'http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/story_list/' + str(author_id)

    reply = requests.get(url, timeout=1)
    json_data = reply.json()
    if json_data["result"] == 1:
        return json_data["stories"]
    else:
        return []