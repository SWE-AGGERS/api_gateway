from flask import Blueprint, render_template
from flask_login import current_user, login_required
from service.constants import FOLLOWING_LIST_URL
import requests

followers = Blueprint('followers', __name__)

@followers.route('/followers/list', methods=['GET'])
@login_required
def _followers_list():
    subject = current_user.id

    temp = get_following_list_s()
    followers = []

    for f in temp:
        d = {"id": f[1].id, "firstname": f[1].firstname,
             "lastname": f[1].lastname}
        followers.append(d)

    return render_template("follower.html", followers=followers, wall_url="/wall")



def get_following_list_s():
    url = FOLLOWING_LIST_URL + str(current_user.id)
    reply = requests.get(url, timeout=5)
    json_data = reply.json()
    return json_data["followed"]