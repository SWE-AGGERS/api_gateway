from flask import abort, json

from flask import Blueprint, render_template, request
from service.auth import current_user #??
from requests.exceptions import Timeout
from flask_login import (current_user, login_required)

from service.constants import STORIES_SERVICE_IP, STORIES_SERVICE_PORT, USERS_SERVICE_IP, USERS_SERVICE_PORT, DICE_SERVICE_IP, DICE_SERVICE_PORT
from service.forms import StoryForm, SelectDiceSetForm, StoryFilter
#from service.database import db, Story, Reaction, User
from service.classes.DiceSet import DiceSet, WrongDiceNumberError, NonExistingSetError, WrongArgumentTypeError
from service.views.home import index
#from service.views.check_stories import check_storyV2, InvalidStory, TooLongStoryError, TooSmallStoryError, WrongFormatDiceError, WrongFormatSingleDiceError, WrongFormatStoryError
import re

storiesbp = Blueprint('stories', __name__)


@storiesbp.route('/stories', methods=['POST', 'GET'])
@login_required
def _stories(message='', error=False, res_msg='', info_bar=False):
    # TODO delete
    current_user.id = 1
    form = SelectDiceSetForm()
    if 'POST' == request.method:
        # Create a new story
        new_story = Story()
        new_story.author_id = current_user.id
        new_story.likes = 0
        new_story.dislikes = 0

        if form.validate_on_submit():
            text = request.form.get('text')
            roll = request.form.get('roll')
            # for the tests
            if re.search('"', roll):
                roll = json.loads(request.form.get('roll'))

        if (type(roll) is str):
            roll = roll.replace("[", "")
            roll = roll.replace("]", "")
            roll = roll.replace("'", "")
            roll = roll.replace(" ", "")
            aux = roll.split(",")
            roll = aux

        dicenumber = len(roll)
        try:
            check_storyV2(text, roll)
            new_story.text = text
            new_story.roll = {'dice': roll}
            new_story.dicenumber = dicenumber
            db.session.add(new_story)
            db.session.commit()
        except WrongFormatStoryError:
            # print('ERROR 1', file=sys.stderr)
            message = "There was an error. Try again."
            
        except WrongFormatDiceError:
            # print('ERROR 2', file=sys.stderr)
            message = "There was an error. Try again."
            
        except TooLongStoryError:
            # print('ERROR 3', file=sys.stderr)
            message = "The story is too long. The length is > 1000 characters."
            
        except TooSmallStoryError:
            # print('ERROR 4', file=sys.stderr)
            message = "The number of words of the story must greater or equal of the number of resulted faces."
            
        except WrongFormatSingleDiceError:
            # print('ERROR 5', file=sys.stderr)
            message = "There was an error. Try again."

        except InvalidStory:
            # print('ERROR 6', file=sys.stderr)
            message = "Invalid story. Try again!"

        allstories = db.session.query(Story, User).join(User).all()
        allstories = list(
            map(lambda x: (
                x[0],
                x[1],
                "hidden" if x[1].id == current_user.id else "",
                "unfollow" if is_follower_s(current_user.id, x[1]['user_id']) else "follow",
                reacted(current_user.id, x[0].id)
            ), allstories)
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
            current_user=current_user.id
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
            current_user=current_user.id
        )


def get_stories_s():
    # call story service
    reply = request.get('http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/stories', timeout=1)
    body = json.loads(str(reply.data, 'utf8'))
    return body['stories']


def get_users_s(_id):
    url = 'http://' + USERS_SERVICE_IP + ':' + USERS_SERVICE_PORT + '/user/' + str(_id)
    # TODO error
    reply = request.get(url, timeout=1)
    user = json.loads(str(reply.data, 'utf8'))
    return user

def is_follower_s(user_a, user_b):
    #check if user_a follow user_b
    reply = request.get('http://' + USERS_SERVICE_IP + ':' + USERS_SERVICE_PORT +\
                        '/is_follower/' + user_a + '/' + user_b, timeout=1)
    body = json.loads(str(reply.data, 'utf8'))
    return body['follow']


@storiesbp.route('/stories/<storyid>', methods=['GET'])
def get_story_detail(storyid):
    story = get_story_by_id(storyid)
    return render_template("story_detail.html", story=story)


def get_story_by_id(story_id):
    url = 'http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/stories/' + str(storyid)
    reply = request.get(url, timeout=1)
    story =  json.loads(str(reply.data))
    if story["result"] == 1:
        return story["story"]
    else:
        abort(404)


def get_roll(dicenumber, dicesetid):
    url = 'http://' + DICE_SERVICE_IP + ':' + DICE_SERVICE_PORT + '/rolldice' + str(dicenumber) + '/' + str(dicesetid)
    reply = request.get(url)
    roll = json.loads(str(reply.data))
    return roll


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
    try:
        random_story = get_random_story()
    except:
        random_story = Story()
    #return None # TODO: which return is the right one?
    #return redirect('/stories/'+str(random_story_from_db.id))
    return render_template("story_detail.html", story=random_story)

def get_random_story():
    url = 'http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/stories/random'
    reply = request.get(url, timeout=1)
    reply = json.loads(str(reply.data))
    if reply["result"] == 1:
        return reply["story"]
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
                                       current_user=current_user.id
                                       )
        else:
            return render_template('filter_stories.html',
                                   form=form,
                                   info_bar=True,
                                   error=True,
                                   res_msg='Cant travel back in time! Doublecheck dates')


def get_filtered_stories(init_date, end_date):
    url = 'http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/stories/filter'
    _json = {"init_date": init_date, "end_date": end_date, "userid": current_user.id}
    reply = request.post(url, json=_json, timeout=1)
    reply = json.loads(str(reply.data))
    if reply["result"] == 1:
        return reply["stories"]
    elif reply["result"] == 0:
        return []
    else:
        return None #Raise exception? #TODO



class StoryNonExistsError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def reacted(user_id, story_id):
    q = db.session.query(Reaction).filter_by(
        story_id=story_id, user_id=user_id).all()
    
    if len(q) > 0:
        return q[0].type
    return 0


@storiesbp.route('/stories/<storyid>/remove/<page>', methods=['POST'])
@login_required
def remove_story(story_id, page):
    if call_remove_story_s(story_id):
        # Removed correctly
        # ? remove reactions of story_id ?
        message = 'The story has been canceled.'
        if page == 'stories':
            return redirect('/stories')
        else:
            return index()
    else:
        # NOT Removed correctly
        message = 'The story was written by another user and cannot be deleted.'
        return redirect('/stories')
    


def call_remove_story_s(story_id):
    url = 'http://' + STORIES_SERVICE_IP + ':' + STORIES_SERVICE_PORT + '/stories/remove/' + str(story_id)
    try:
        reply = request.post(url, args={'userid': current_user.id}, timeout=1)
    except Timeout:
        return False

    reply = json.loads(str(reply.data))

    return reply["result"] == 0

"""
@storiesbp.route('/stories/<storyid>/remove/<page>', methods=['POST'])
@login_required
def get_remove_story(storyid,page):
    error = False
    res_msg = ''
    info_bar = False
    # Remove story
    q = db.session.query(Story).filter_by(id=storyid)
    story = q.first()
    if story is not None:
        if story.author_id == current_user.id:
            reactions = Reaction.query.filter_by(story_id=storyid).all()
            if reactions is not None:
                for reac in reactions:
                        db.session.delete(reac)
                        db.session.commit()
            db.session.delete(story)
            db.session.commit()
            #return redirect('/')
            if page == "stories":
                message = "The story has been canceled."
                #return _stories(message)
                form = SelectDiceSetForm()
                allstories = db.session.query(Story, User).join(User).all()
                allstories = list(
                    map(lambda x: (
                        x[0],
                        x[1],
                        "hidden" if x[1].id == current_user.id else "",
                        "unfollow" if is_follower_s(current_user.id, x[1]['user_id']) else "follow",
                        reacted(current_user.id, x[0].id)
                    ), allstories)
                )
                for x in allstories:
                    print(x)

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
                    current_user=current_user.id
                )
            else:
                return index()
        else:
            # The user can only delete the stories she/he wrote.
            #abort(404)
            #return redirect('/stories')
            message = "The story was written by another user and cannot be deleted."
            #return _stories(message)
            form = SelectDiceSetForm()
            allstories = db.session.query(Story, User).join(User).all()
            allstories = list(
                map(lambda x: (
                    x[0],
                    x[1],
                    "hidden" if x[1].id == current_user.id else "",
                    "unfollow" if is_follower_s(current_user.id, x[1]['user_id']) else "follow",
                    reacted(current_user.id, x[0].id)
                ), allstories)
            )
            for x in allstories:
                print(x)

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
                current_user=current_user.id
            )

    else:
        # Story doesn't exist
        abort(404)
"""
