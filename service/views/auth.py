from flask import Blueprint, render_template, redirect
from flask_login import (current_user, login_user, logout_user, login_required)
from service.database import db, User
from service.forms import LoginForm
from service.forms import UserForm
from service.constants import USERS_SERVICE_IP, USERS_SERVICE_PORT
import requests
from flask import request
auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    message = ""
    error = False

    if form.validate_on_submit():
        url = "http://{}:{}/login".format(USERS_SERVICE_IP, USERS_SERVICE_PORT)
        data = {"email": form.email.data, "password": form.password.data}
        headers = {'Content-type': 'application/json; charset=UTF-8'}

        call_user = requests.post(url, json=data,headers=headers)

        if call_user.json["response"]:
            user = User()
            user.id = call_user.json()["user_id"]
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
        email = form.data['email']


        url = "http://{}:{}/login".format(USERS_SERVICE_IP, USERS_SERVICE_PORT)

        headers = {'Content-type': 'application/json; charset=UTF-8'}
        user = User()
        user.firstname = form.data['firstname']
        user.lastname = form.data['lastname']
        user.email = form.data['email']
        user.dateofbirth = form.data['dateofbirth']
        user.set_password(form.data['password'])

        data ={
                "firstname" : user.firstname,
                "lastname": user.lastname,
                "email" : user.email,
                "dateofbirth":{
                    "year": user.dateofbirth.year,
                    "month":user.dateofbirth.month ,
                    "day":user.dateofbirth.day
                },
                "password": form.data['password']
                }

        call_user = requests.post(url, json=data,headers=headers)

        if not call_user.json()["error"]:
            user.id = call_user.json()["user_id"]
            login_user(user)
            return redirect("/")
        else:
            form = UserForm()

            return render_template('signup.html', form=form, error=True, message="The email was used before. Please change the email!")
    if request.method == 'GET':
        return render_template('signup.html', form=form)
