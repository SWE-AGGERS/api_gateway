from service.classes.Stories import Stories, Story
from service.classes.User import User
from service.classes.Utils import getStories


class Stats(dict):
    user: dict

    numStories: int
    likes: int
    dislikes: int
    numDice: int

    avgLike: float
    avgDislike: float
    avgDice: float

    ratio_likeDislike: float
    love_level: int

    def __init__(self, body: dict):
        super().__init__()
        if body.get('user') is None:
            return

        self.user = body['user']

        self.numStories = body['numStories']
        self.likes = body['likes']
        self.dislikes = self['dislikes']
        self.numDice = self['numDice']

        self.avgLike = self['avgLike']
        self.avgDislike = self['avgDislike']
        self.avgDice = self['avgDice']

        self.ratio_likeDislike = self['ratio_likeDislike']
        self.love_level = self['love_level']

    def jsonify(self):
        self['user'] = self.user

        self['numStories'] = self.numStories
        self['likes'] = self.likes
        self['dislikes'] = self.dislikes
        self['numDice'] = self.numDice

        self['avgLike'] = self.avgLike
        self['avgDislike'] = self.avgDislike
        self['avgDice'] = self.avgDice

        self['ratio_likeDislike'] = self.ratio_likeDislike
        self['love_level'] = self.love_level

        return self
