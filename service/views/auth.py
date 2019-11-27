from flask import Blueprint, render_template, redirect, json
from flask_login import (current_user, login_user, logout_user, login_required)
from service.classes.User import  User
from service.forms import LoginForm
from service.forms import UserForm
from service.constants import LOGIN_URL, SIGNUP_URL
import requests
from flask import request
auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    message = ""
    error = False

    if form.validate_on_submit():
        url = LOGIN_URL
        data = {"email": form.email.data, "password": form.password.data}
        headers = {'Content-type': 'application/json; charset=UTF-8'}

        call_user = requests.post(url, json=data,headers=headers)
        print(call_user.json()["response"])

        if call_user.json()["response"]:
            json_data = call_user.json()

            user = User(user_id=json_data["user_id"],
                        firstname=json_data["firstname"],
                        lastname=json_data["lastname"],
                        email=json_data["email"],
                        dateofbirth=json_data["dateofbirth"],
                        token=json_data["auth_token"],
                        is_active=json_data["is_active"],
                        is_admin=json_data["is_admin"],
                        authenticated=json_data["is_authenticated"]
                        )
            login_user(user)
            return redirect('/')
        else:
            message = "User not found"
            error = True

    return render_template('login.html', form=form, error=error, message=message)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect('/')


@auth.route("/signup", methods=['POST', 'GET'])
def signup():

    form = UserForm()

    if request.method == 'POST':

        headers = {'Content-type': 'application/json; charset=UTF-8'}
        date = "{}".format(form.data["dateofbirth"]).split("-")
        data = {
                "firstname" : form.data['firstname'],
                "lastname": form.data['lastname'],
                "email" : form.data["email"],
                "dateofbirth": {
                    "year": date[2],
                    "month": date[1],
                    "day": date[0]
                },
                "password": form.data["password"]
                }
        singup_request = requests.post(SIGNUP_URL, json=data, headers=headers)
        try:
            data = singup_request.json()
        except:
            raise Exception(singup_request)
        print(data)
        if not singup_request.json()["error"]:
            user = User(user_id=data["user_id"],
                        firstname=data["firstname"],
                        lastname=data["lastname"],
                        email=data["email"],
                        dateofbirth=data["dateofbirth"],
                        token=data["auth_token"],
                        is_active=data["is_active"],
                        is_admin=data["is_admin"],
                        authenticated=data["is_authenticated"]
                        )
            login_user(user)
            return redirect("/")
        else:
            form = UserForm()

            return render_template('signup.html', form=form, error=True, message="The email was used before. Please change the email!")
    if request.method == 'GET':
        return render_template('signup.html', form=form)
