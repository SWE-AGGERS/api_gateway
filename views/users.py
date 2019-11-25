from flask import Blueprint, redirect, render_template, request

from api_gateway.database import db, User, Story
from api_gateway.forms import UserForm
from flask_login import current_user
from sqlalchemy import desc
from api_gateway.views.follow import _is_follower
from api_gateway.views.stories import reacted

users = Blueprint('users', __name__)

@users.route('/users')
def _users():
    users = get_users_s()
    user_stories = []
    for user in users:
        user_stories.append((get_stories_s(user["id"], limit=1)[0], user))
    
    users = list(
        map(lambda x: (
            x[0],
            x[1],
            "hidden" if x[1]["id"] == current_user.id else "",
            "unfollow" if _is_follower(current_user.id, x[1]["id"]) else "follow",
            reacted(current_user.id, x[0]["id"])
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
        reply = request.get('http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/story_list/'+str(userid)+'/'+str(limit), timeout=1)
    else:
        reply = request.get('http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/story_list/'+str(userid), timeout=1)
    body = json.loads(str(reply.data, 'utf8'))
    # Gestire errori in base al campo result di body
    return body['stories']


def get_users_s():
    """Get the list of all users"""
    url = 'http://' + USERS_SERVICE_IP + ':' + USERS_SERVICE_PORT + '/users'
    # TODO error
    reply = request.get(url, timeout=1)
    return json.loads(str(reply.data, 'utf8'))