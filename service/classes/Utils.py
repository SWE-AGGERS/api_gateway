import requests
from requests import Response

from service.classes.Errors import UserException, StoriesException, ServiceUnreachable
from service.classes.Stories import Stories
from service.classes.User import User
from service.constants import STORIES_URL, USER_URL



def getStories(id:int):
    req: Response
    print('Send request to ' + STORIES_URL + ' to update story list')
    try:
        req = requests.get(url=STORIES_URL+str(id), timeout=3)
        print('HTTP.GET executed')
    except TimeoutError:
        print('HTTP.GET FAIL!!!')
        # raise ServiceUnreachable('Story')
        print(ServiceUnreachable('Story'))

    if req.status_code != 200:
        print('Get stories fail with code:' + str(req.status_code))
        return Stories(None)

    stories: Stories = Stories(req.data)
    return stories

def getUser(user_id: int):
    print('Send request to ' + USER_URL + ' to get user details')
    try:
        req = requests.get(USER_URL + str(user_id), timeout=3)
        print('HTTP.GET executed')
    except TimeoutError:
        print('HTTP.GET FAIL!!!')
        raise ServiceUnreachable('User')

    if req.status_code != 200:
        raise UserException('Get user fail with code:' + str(req.status_code))
    data = req.json()
    u: User = User(user_id=data["user_id"], 
        firstname=data["firstname"], 
        lastname=data["lastname"], 
        email=data["email"], 
        is_active=True, 
        is_admin=True,
        dateofbirth=data["dateofbirth"], 
        token=data["auth_token"], 
        authenticated=True)

    return u