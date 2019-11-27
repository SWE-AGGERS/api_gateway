from flask import Blueprint, redirect, render_template, request, json

from flask_login import current_user
import requests
from service.views.stories import reacted

from service.constants import STORIES_SERVICE_IP, STORIES_SERVICE_PORT, USERS_SERVICE_IP, USERS_SERVICE_PORT

users = Blueprint('users', __name__)

@users.route('/users')
def _users():
    users = get_users_s()["result"]
    user_stories = []
    for user in users:
        t = get_stories_s(user["user_id"], limit=1)
        if len(t) > 0:
            user_stories.append((t, user))
    
    users = list(
        map(lambda x: (
            x[0],
            x[1],
            "hidden" if x[1]['user_id'] == current_user.id else "",
            "unfollow" if is_follower_s(current_user.id, x[1]['user_id']) else "follow",
            reacted(current_user.id, x[0]['id'])
        ), user_stories)
    )
    
    return render_template(
        "users.html",
        stories=users,
        like_it_url="/stories/reaction",
        details_url="/stories"
    )


def get_stories_s(userid, limit=0):
    # call story service

    if limit > 0:
        reply = requests.get('http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/story_list/'+str(userid)+'/'+str(limit), timeout=5)
    else:
        reply = requests.get('http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/story_list/'+str(userid), timeout=5)

    body = reply.json()
    # Gestire errori in base al campo result di body
    if body['result'] == 1:
        return body['stories'][0]
    else:
        return []


def get_users_s():
    #Get the list of all users
    url = 'http://' + USERS_SERVICE_IP + ':' + USERS_SERVICE_PORT + '/users'
    # TODO error
    reply = requests.get(url, timeout=1)
    return reply.json()


def is_follower_s(user_a, user_b):
    #check if user_a follow user_b
    reply = requests.get('http://' + USERS_SERVICE_IP + ':' + USERS_SERVICE_PORT +\
                        '/is_follower/' + str(user_a) + '/' + str(user_b), timeout=1)
    body = reply.json()
    return body['follow']
