from .auth import auth
from .followers import followers
from .home import home
from .stories import storiesbp
from .users import users
from .wall import wall
#from .search import search

blueprints = [auth, home, storiesbp, wall, users, followers]
