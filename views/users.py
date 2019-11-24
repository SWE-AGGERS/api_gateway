from flask import Blueprint, redirect, render_template, request

from api_gateway.database import db, User, Story
from api_gateway.forms import UserForm
from flask_login import current_user
from sqlalchemy import desc
from api_gateway.views.follow import _is_follower
from api_gateway.views.stories import reacted

users = Blueprint('users', __name__)


# Reducing the join (User x Story on user.id = story.author_id) 
# to a list of <User, Latest User's Story>
def reduce_list(users_):
    users = []
    aux = []
    for story, user in users_:
        if user.id not in aux:
            users.append(
                (story, user)
            )
            aux.append(user.id)

    return users


@users.route('/users')
def _users():
    users = db.session.query(Story, User).join(Story).order_by(desc(Story.id))
    users = reduce_list(users.all())

    users = list(
        map(lambda x: (
            x[0],
            x[1],
            "hidden" if x[1].id == current_user.id else "",
            "unfollow" if _is_follower(current_user.id, x[1].id) else "follow",
            reacted(current_user.id, x[0].id)
        ), users)
    )
    
    return render_template(
        "users.html",
        stories=users,
        like_it_url="/stories/reaction",
        details_url="/stories"
    )
