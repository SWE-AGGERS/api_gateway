from flask import abort, json, jsonify
from flask import Blueprint, render_template, request
from requests.exceptions import Timeout
from flask_login import (current_user, login_required)
from service.constants import STORIES_SERVICE_IP, STORIES_SERVICE_PORT, USERS_SERVICE_IP, USERS_SERVICE_PORT, DICE_SERVICE_IP, DICE_SERVICE_PORT, REACTIONS_SERVICE_IP, REACTIONS_SERVICE_PORT
from service.forms import StoryForm, SelectDiceSetForm, StoryFilter
from service.views.home import index

from service.classes.Stories import DetailedStory
import requests
import re

storiesbp = Blueprint('stories', __name__)


@storiesbp.route('/stories', methods=['POST', 'GET'])
@login_required
def _stories(message='', error=False, res_msg='', info_bar=False):
    # TODO delete
    form = SelectDiceSetForm()
    if 'POST' == request.method:

        if form.validate_on_submit():
            text = request.form.get('text')
            roll = request.form.get('roll')
            # for the tests
            if re.search('"', roll):
                roll = json.loads(request.form.get('roll'))

        roll = ["bird", "whale", "coffee", "bananas", "ladder", "glasses"]
        reply = requests.post('/stories?userid='+str(current_user.id), data=json.dumps({'created_story': {
            'text': text, 'roll': roll}}), content_type='application/json')
        if reply.status_code == 200:
            body = json.loads(str(reply.data, 'utf8'))
            message = body['message']
        else:
            message = "Error connecting with stories service"
        allstories = list(
            map(lambda x: (
                x[0],
                x[1],
                "hidden" if x[1].id == current_user.id else "",
                "unfollow" if is_follower_s(current_user.id, x[1]['user_id']) else "follow",
                reacted(current_user.id, x[0].id)
            ), body['stories'])
        )
        return render_template(
            "stories.html",
            message=message,
            form=form,
            stories=allstories,
            active_button="stories",
            like_it_url="/stories/reaction",
            details_url="/stories",
            error=error,
            info_bar=info_bar,
            res_msg=str(res_msg),
            current_user=current_user.id,
            token_jwt=current_user.token
        )
    elif 'GET' == request.method:
        stories = get_stories_s()
        users = []
        for _id in list(map(lambda story: story['author_id'], stories)):
            user = get_users_s(str(_id))
            users.append(user)

        allstories = list(
            map(lambda x: (
                x[0],
                x[1],
                "hidden" if x[1]['user_id'] == current_user.id else "",
                "unfollow" if is_follower_s(current_user.id, x[1]['user_id']) else "follow",
                reacted(current_user.id, x[0]['id'])
            ), zip(stories, users))
        )

        return render_template(
            "stories.html",
            message=message,
            form=form,
            stories=allstories,
            active_button="stories",
            like_it_url="/stories/reaction",
            details_url="/stories",
            error=error,
            info_bar=info_bar,
            res_msg=str(res_msg),
            current_user=current_user.id,
            token_jwt=current_user.token
        )


def get_stories_s():
    url = 'http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/stories'
    reply = requests.get(url, timeout=1)
    json_data = reply.json()
    if json_data['result'] == 1:
        return json_data['stories']
    else:
        return []


def get_users_s(_id):
    url = 'http://' + USERS_SERVICE_IP + ':' + USERS_SERVICE_PORT + '/user/' + str(_id)
    reply = requests.get(url, timeout=1)
    json_data = reply.json()
    return json_data

def is_follower_s(user_a, user_b):
    url = 'http://' + USERS_SERVICE_IP + ':' + USERS_SERVICE_PORT + '/is_follower/' + str(user_a) + '/' + str(user_b)
    reply = requests.get(url, timeout=1)
    json_data = reply.json()
    return json_data['follow']


@storiesbp.route('/stories/<storyid>', methods=['GET'])
def get_story_detail(storyid):
    story = get_story_by_id(storyid)
    return render_template("story_detail.html", story=story)


def get_story_by_id(story_id):
    url = 'http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/stories/' + str(story_id)
    reply = requests.get(url, timeout=1)
    json_data = reply.json()
    if json_data["result"] == 1:
        return json_data["story"]
    else:
        abort(404)


def get_roll(dicenumber, dicesetid):
    """
    Calls the DiceManagement service in order to roll <dicenumber> from the dice set <dicesetid>
    """
    url = 'http://' + DICE_SERVICE_IP + ':' + DICE_SERVICE_PORT + '/rolldice' + str(dicenumber) + '/' + str(dicesetid)
    reply = requests.get(url)
    json_data = reply.json()
    return json_data


 # TODO
@storiesbp.route('/rolldice/<dicenumber>/<dicesetid>', methods=['GET'])
def _roll(dicenumber, dicesetid):
    form = StoryForm()

    # Get the roll info (message, diceset and roll, which is an array of strings representing the faces) 
    roll_info = get_roll(dicenumber, dicesetid)

    if(roll_info["message"]=="Correct roll"):
        roll = roll_info["roll"]
        phrase = ""
        for elem in roll:
            phrase = phrase + elem + " "
        return render_template("create_story.html", form=form, set=dicesetid, roll=roll, phrase=phrase)
    elif(roll_info["message"]=="Dice number needs to be an integer!"):
        return _stories("<div class=\"alert alert-danger alert-dismissible fade show\">" +
                        "<button type=\"button\" class=\"close\" data-dismiss=\"alert\">&times;</button>" +
                        "<strong>Error!</strong> Argument Dice number needs to be an integer!</div>")
    elif(roll_info["message"] == "Wrong dice number!"):
        return _stories("<div class=\"alert alert-danger alert-dismissible fade show\">" +
                        "<button type=\"button\" class=\"close\" data-dismiss=\"alert\">&times;</button>" +
                        "<strong>Error!</strong> Wrong dice number!</div>")
    elif(roll_info["message"] == "Dice set " + str(dicesetid) + " doesn't exist!" ):
        abort(404)

@storiesbp.route('/stories/random', methods=['GET'])
def random_story():

    random_story = DetailedStory(get_random_story())
    return render_template("story_detail.html", story=random_story)


def get_random_story():
    url = 'http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/stories/random'
    reply = requests.get(url, timeout=5)
    json_data = reply.json()
    if json_data["result"]:
        return json_data["story"]
    else:
        raise StoryNonExistsError('Story not exists!')



@storiesbp.route('/stories/filter', methods=['GET', 'POST'])
@login_required
def filter_stories():
    if request.method == 'GET':
        form = StoryFilter()
        return render_template('filter_stories.html', form=form)
    if request.method == 'POST':
        form = StoryFilter()
        if form.validate_on_submit():
            init_date = form.init_date.data
            end_date = form.end_date.data
            f_stories = get_filtered_stories(init_date, end_date)
            if f_stories is not None:
                f_stories = list(
                    map(lambda x: (
                        x[0],
                        x[1],
                        "hidden" if x[1]["id"] == current_user.id else "",
                        "unfollow" if is_follower_s(current_user.id, x[1]['user_id']) else "follow",
                        reacted(current_user.id, x[0]["id"])
                    ), f_stories))
                return render_template('filter_stories.html',
                                       form=form,
                                       stories=f_stories,
                                       active_button="/stories",
                                       like_it_url="/stories/reaction",
                                       details_url="/stories",
                                       error=False,
                                       info_bar=False,
                                       c_user=current_user,
                                       current_user=current_user.id,
                                       token_jwt=current_user.token
                                       )
        else:
            return render_template('filter_stories.html',
                                   form=form,
                                   info_bar=True,
                                   error=True,
                                   res_msg='Cant travel back in time! Doublecheck dates')


def get_filtered_stories(init_date, end_date):
    url = 'http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/stories/filter'

    # Filter correctly a time interval
    data = json.dumps({'info': {'userid': current_user.id, 'init_date': init_date, 'end_date': end_date}})
    reply = requests.post(url, json=json.dumps({'info': {'userid': current_user.id, 'init_date': init_date, 'end_date': end_date}}))

    body = reply.json()

    if body["result"] == 1:
        return body["stories"]
    elif body["result"] == 0:
        return []
    else:
        return [] #Raise exception? #TODO



class StoryNonExistsError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)




@storiesbp.route('/stories/<storyid>/remove/<page>', methods=['POST'])
@login_required
def remove_story(story_id, page):
    reply = call_remove_story_s(story_id,current_user.id)
    arr = get_stories_s()
    info_bar = False
    res_msg = ''
    form = SelectDiceSetForm()
    message = reply['message']
    if page == 'stories':
        return render_template(
            "stories.html",
            message=message,
            form=form,
            stories=arr,
            active_button="stories",
            like_it_url="/stories/reaction",
            details_url="/stories",
            error=reply['result'],
            info_bar=info_bar,
            res_msg=str(res_msg),
            current_user=current_user.id,
            token_jwt=current_user.token)
    else:
        return index()
    


def call_remove_story_s(story_id, user_id):

    url = 'http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/stories/remove/' + str(story_id) + "?userid=" + str(user_id)
    reply = requests.post(url)
    body = json.loads(str(reply.data, 'utf8'))
    return body


def reacted(user_id, story_id):
    url = 'http://' + REACTIONS_SERVICE_IP + ':' + REACTIONS_SERVICE_PORT + '/reacted_on/'+ str(story_id) + '/' + str(user_id)



