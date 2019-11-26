import requests
from requests import Response

from service.classes.Errors import UserException, StoriesException, ServiceUnreachable
from service.classes.Stories import Stories

ENDPOINT_STORIES = 'http://0.0.0.0:5042/stories/'



def getStories(id:int):
    req: Response
    print('Send request to ' + ENDPOINT_STORIES + ' to update story list')
    try:
        req = requests.get(url=ENDPOINT_STORIES+str(id), timeout=3)
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

