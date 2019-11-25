"""
from flask import Blueprint, render_template

from service.auth import current_user
from service.database import db, Story

from service.constants import STORIES_SERVICE_IP, STORIES_SERVICE_PORT


home = Blueprint('home', __name__)


def _strava_auth_url(config):
    return '127.0.0.1:5000'


@home.route('/')
def index():
    if current_user is not None and hasattr(current_user, 'id'):
        stories = dget_story_by_author_id(current_user.id)
    else:
        stories = None
    return render_template("index.html", stories=stories, active_button="index")

def get_story_by_author_id(author_id):
    url = 'http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/story_list/' + str(author_id)
    try:
	    reply = request.get(url, timeout=1)
	    story =  json.loads(str(reply.data))
	    if story["result"] == 1:
	        return story["story"]
	    else:
	        return None
	except:
		return None
"""