import json


class Story(dict):
    id: int
    text: str
    dicenumber:int
    roll: list

    date: str
    likes: int
    dislikes:int
    author_id: int

    def __init__(self, storydict: dict):
        super().__init__()
        self.id = storydict['id']
        self.text = storydict['text']
        self.dicenumber = storydict['dicenumber']
        self.roll = storydict['roll']
        self.date = storydict['date']
        self.likes = storydict['likes']
        self.dislikes = storydict['dislikes']
        self.author_id = storydict['author_id']

    def jsonify(self):
        self['id'] = self.id
        self['text'] = self.text
        self['dicenumber'] = self.dicenumber
        self['roll'] = self.roll
        self['date'] = self.date
        self['likes'] = self.likes
        self['dislikes'] = self.dislikes
        self['author_id'] = self.author_id

        return self


class Stories(dict):
    storylist:list

    def __init__(self, jpayload: json):
        super().__init__()
        self.storylist = []
        if jpayload is None:
            return

        stories = json.loads(str(jpayload, 'utf8'))

        for s in stories['stories']:
            story: Story = Story(s)
            self.storylist.append(story)

    def jsonify(self):
        ls: list = []

        for s in self.storylist:
            s: Story
            ls.append(s.jsonify())

        self['stories'] = ls

        return self
