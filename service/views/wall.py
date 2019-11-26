import json

import requests
from flask import Blueprint, render_template, jsonify
from flask_login import login_required

from service.classes.Stats import Stats
from service.classes.User import User
from service.classes.Wall import Wall
from service.auth import current_user
from service.forms import SelectDiceSetForm

from service.views.stories import reacted

ENDPOINT_STATS = 'http://localhost:5004/stats/'

ENDPOINT_STORIES = 'http://localhost:500x/story_list/'

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

    reply = requests.get(ENDPOINT_STATS + str(user_id))

    if reply.status_code != 200:
        error = json.loads(str(reply.data, 'utf8'))
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
            user=User(),
            stats=Stats({})
        )
        return rend

    try:
        stats_js = json.loads(str(reply.data, 'utf8'))
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
            user=User(),
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
            user=User(),
            stats=Stats({})
        )
        return rend

    stats = Stats(stats_js)

    try:
        reply = requests.get(ENDPOINT_STORIES + str(user_id))
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
            user=User(),
            stats=Stats({})
        )
        return rend

    stories = body['stories']

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
        user=stats['user'],
        stats=stats
    )

    return rend


@wall.route('/thewall/<user_id>', methods=['GET'])
@login_required
def getawall(user_id):
    # if user_id < 0:
    #     return User_not_found()
    q = db.session.query(User).filter(User.id == user_id)
    user = q.first()
    if user is None:
        return User_not_found()

    q = db.session.query(Story).filter(Story.author_id == user.id)
    thewall: Wall = Wall(user)
    user_stories = []
    for s in q:
        s: Story
        thewall.add_story(s)
        user_stories.append(
            {'story_id': s.id,
             'text': s.text,
             'likes': s.likes,
             'dislikes': s.dislikes
             })
        #user_stories.append(s)

    return jsonify(firstname=user.firstname,
                   lastname=user.lastname,
                   id=user.id,
                   email=user.email,
                   stories=user_stories) # thewall.stories

