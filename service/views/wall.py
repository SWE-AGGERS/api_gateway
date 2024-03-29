import json

import requests
from flask import Blueprint, render_template, jsonify
from flask_login import login_required

from service.classes.Stats import Stats
from service.classes.Stories import Stories
from service.classes.User import User

from service.classes.Utils import getUser, getStories
from service.auth import current_user
from service.forms import SelectDiceSetForm

from service.views.stories import reacted
from service.constants import STATS_URL, STORIES_LIST_URL, GET_USER_URL


wall = Blueprint('wall', __name__)

def User_not_found():
    return render_template("user_not_found.html")


def _strava_auth_url(config):
    return '127.0.0.1:5000'


# @wall.route('/wall/user_email', methods=['GET'])
# @login_required
# def get_wall_email(user_email):
#     if current_user is not None and hasattr(current_user, 'id'):
#         q = db.session.query(User).filter(User.email == user_email)
#         user = q.first()
#         if user is None:
#             return User_not_found()
#         return render_wall(user.id)


@wall.route('/wall', methods=['GET'])
@login_required
def getmywall():
    if current_user is not None and hasattr(current_user, 'id'):
        return render_wall(current_user.id)


@wall.route('/wall/<user_id>', methods=['GET'])
@login_required
def render_wall(user_id):
    form = SelectDiceSetForm()

    reply = requests.get(STATS_URL + str(user_id))


    if reply.status_code != 200:
        error = reply.json()
        rend = render_template(
            "wall.html",
            message=str(error),
            form=form,
            stories=[],
            active_button="stories",
            like_it_url="/stories/reaction",
            details_url="/stories",
            error=True,
            info_bar=False,
            res_msg=str(''),
            user=getUser(user_id),
            stats=Stats({})
        )
        return rend

    try:
        stats_js = reply.json()
    except Exception as e:
        rend = render_template(
            "wall.html",
            message=str(e),
            form=form,
            stories=[],
            active_button="stories",
            like_it_url="/stories/reaction",
            details_url="/stories",
            error=True,
            info_bar=False,
            res_msg=str(''),
            user=getUser(user_id),
            stats=Stats({})
        )   
        return rend

    if stats_js.get('user') is None:
        rend = render_template(
            "wall.html",
            message='Stats not retrieved',
            form=form,
            stories=[],
            active_button="stories",
            like_it_url="/stories/reaction",
            details_url="/stories",
            error=True,
            info_bar=False,
            res_msg=str(''),
            user=getUser(user_id),
            stats=Stats({})
        )
        return rend

    stats = Stats(stats_js)
    user_js = stats.user
    user: User = User(
        user_id=user_js['user_id'],
        firstname=user_js['firstname'],
        lastname=user_js['lastname'],
        email=user_js['email']
    )

    try:
        reply = requests.get(STORIES_LIST_URL + str(user_id))
        body = json.loads(str(reply.data, 'utf8'))
    except Exception as e:
        rend = render_template(
            "wall.html",
            message=str(e),
            form=form,
            stories=[],
            active_button="stories",
            like_it_url="/stories/reaction",
            details_url="/stories",
            error=True,
            info_bar=False,
            res_msg=str(''),
            user=user,
            stats=Stats({})
        )
        return rend

    stories = Stories(reply.data)

    if body['result'] < 1:
        rend = render_template(
            "wall.html",
            message=body['message'],
            form=form,
            stories=stories.storylist,
            active_button="stories",
            like_it_url="/stories/reaction",
            details_url="/stories",
            error=True,
            info_bar=False,
            res_msg=str(''),
            user=user,
            stats=stats
        )

        return rend

    rend = render_template(
        "wall.html",
        message='',
        form=form,
        stories=stories,
        active_button="stories",
        like_it_url="/stories/reaction",
        details_url="/stories",
        error=False,
        info_bar=False,
        res_msg=str(''),
        user=user,
        stats=stats
    )

    return rend
