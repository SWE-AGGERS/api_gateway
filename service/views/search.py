from flask import Blueprint, render_template
from flask import request
import json
import requests
from requests import Timeout
from service.constants import STORIES_SERVICE_IP, STORIES_SERVICE_PORT, USERS_SERVICE_IP, USERS_SERVICE_PORT
from service.constants import TIMEOUT



search = Blueprint('search', __name__)


@search.route('/search', methods=["GET"])
def index():
    search_text = request.args.get("search_text")
    if search_text:
        users = find_user(text=search_text)
        stories = find_story(text=search_text)
        if users and len(stories) > 0:
            return render_template("search.html", users=users, stories=stories)
        elif users:
            return render_template("search.html", users=users)
        elif stories:
            return render_template("search.html", stories=stories)
        else:
            return render_template("search.html")
    else:
        return render_template("search.html")


def find_user(text):
    try:
        url = 'http://' + USERS_SERVICE_IP + ':' + USERS_SERVICE_PORT + '/search/'+text
        reply = requests.get(url,timeout = TIMEOUT)
        json_data = reply.json()
        return json_data
    except Timeout:
        return None


def find_story(text):
    try:
        url = 'http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/search_story'
        reply = requests.get(url,data=json.dumps({"story": {"text": text}}),content_type='application/json',timeout = TIMEOUT)
        json_data = reply.json()
        if json_data['result'] == 1:
            return json_data['stories']
        else:
            return []
    except Timeout:
        return []
