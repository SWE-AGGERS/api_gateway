class UserException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ServiceUnreachable(Exception):
    def __init__(self, service_name: str):
        self.value = service_name

    def __str__(self):
        return self.value + 'Service Unreachable'


class StoriesException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NoUser(dict):
    def __init__(self):
        super().__init__()
        self['code'] = 404
        self['status'] = 'error'
        self['data'] = 'User not exist'


class NoStats(dict):
    def __init__(self):
        super().__init__()
        self['code'] = 403
        self['status'] = 'error'
        self['data'] = 'Stats not ready'
