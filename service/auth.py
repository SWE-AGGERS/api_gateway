import functools
from flask_login import current_user, LoginManager
from service.constants import GET_USER_URL
import requests
from service.classes.User import User

login_manager = LoginManager()

def admin_required(func):
    @functools.wraps(func)
    def _admin_required(*args, **kw):
        admin = current_user.is_authenticated and current_user.is_admin
        if not admin:
            return login_manager.unauthorized()
        return func(*args, **kw)

    return _admin_required


@login_manager.user_loader
def load_user(user_id):
    headers = {'Content-type': 'application/json; charset=UTF-8'}
    call_user = requests.get("{}/{}".format(GET_USER_URL, user_id), headers=headers)
    data = call_user.json()
    user = User(user_id=data["user_id"],
                firstname=data["firstname"],
                lastname=data["lastname"],
                email=data["email"],
                dateofbirth=data["dateofbirth"],
                token= data["auth_token"],
                is_active=data["is_active"],
                is_admin=data["is_admin"],
                authenticated=data["is_authenticated"]
                )

    if call_user.json()["response"]:

        user._authenticated = True
    return user
