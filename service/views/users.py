
from flask import Blueprint, redirect, render_template, request


from service.forms import UserForm
from flask_login import current_user
from sqlalchemy import desc
import requests
from service.constants import STORIES_SERVICE_IP, STORIES_SERVICE_PORT, USERS_SERVICE_IP, USERS_SERVICE_PORT
from service.constants import FOLLOWERS_SERVICE_IP,FOLLOWERS_SERVICE_PORT
from requests.exceptions import Timeout
import json

users = Blueprint('users', __name__)

@users.route('/users')
def _users():
    users = get_users_s()
    if users == None:
        user_stories = []
    for user in users:
        user_stories.append((get_stories_s(user["id"], limit=1)[0], user))

    """
    
    users = list(
        map(lambda x: (
            x[0],
            x[1],
            "hidden" if x[1]['user_id'] == current_user.id else "",
            "unfollow" if is_follower_s(current_user.id, x[1]['user_id']) else "follow",
            reacted(current_user.id, x[0]['id'])
        ), user_stories)
    )
    
    """
    
    return render_template(
        "users.html",
        stories=users,
        like_it_url="/stories/reaction",
        details_url="/stories"
    )


def get_stories_s(userid, limit=0):
    try:
        if limit > 0:
            url = 'http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/story_list/'+str(userid)+'/'+str(limit)
            reply = requests.get(url, timeout=1)
        else:
            url = 'http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/story_list/'+str(userid)
            reply = requests.get(url, timeout=1)
    except Timeout:
        return None
    body = reply.json()
    if body['result'] == 1:
        return body['stories']
    else:
        return None


def get_users_s():


    try:

        url = 'http://' + USERS_SERVICE_IP + ':' + USERS_SERVICE_PORT + '/users'
        reply = requests.get(url, timeout=1)
    except Timeout:
        return None
    body = reply.json()
    return body




def is_follower_s(user_a, user_b):

    try:

        url = 'http://' + FOLLOWERS_SERVICE_IP + ':' + FOLLOWERS_SERVICE_PORT +'/is_follower/' + user_a + '/' + user_b
        reply = requests.get(url, timeout=1)
    except Timeout:
        return None
    body = reply.json()
    return body['follow']



