from flask import Blueprint, render_template, redirect
from flask_login import (current_user, login_user, logout_user, login_required)
from service.classes.User import  User
from service.forms import LoginForm
from service.forms import UserForm
from service.constants import LOGIN_URL, SIGNUP_URL
import requests
from flask import request
from service.constants import USERS_SERVICE_IP, USERS_SERVICE_PORT
import requests
from requests import Timeout
import json
from service.auth import  current_user



auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    message = ""
    error = False

    if form.validate_on_submit():

        call_user = login_support(form.email.data,form.password.data)

        print(call_user.json()["response"])

        if call_user.json()["response"]:
            return redirect('/')
        else:
            message = "User not found"
            error = True

    return render_template('login.html', form=form, error=error, message=message)


@auth.route("/logout")
def logout():
    call_user = logout_support(current_user.id)

    if call_user.json()["response"]:
        return redirect('/')


@auth.route("/signup", methods=['POST', 'GET'])
def signup():

    form = UserForm()

    if request.method == 'POST':


        error = signup(firstname = form.data['firstname'], lastname = form.data['lastname'], email = form.data['email'], year = form.data.date[2], month = form.data.date[1], day = form.data.date[0], password = form.data['password'])
        if error != None:
            if not error:
                login_support(form.email.data,form.password.data)
                return redirect("/")
            else:
                form = UserForm()
                return render_template('signup.html', form=form, error=True, message="The email was used before. Please change the email!")
        else:
            form = UserForm()
            return render_template('signup.html', form=form, error=True,
                                   message="Timeout user service")

    if request.method == 'GET':
        return render_template('signup.html', form=form)


def login_support(email, password):
    try:
        url = 'http://' + USERS_SERVICE_IP + ':' + USERS_SERVICE_PORT + '/login'
        reply = requests.get(url, data=json.dumps({'email': email, 'password': password}), content_type='application/json')
        json_data = reply.json()
        return json_data['response']
    except Timeout:
        return None




def logout_support(user_id):
    try:
        url = 'http://' + USERS_SERVICE_IP + ':' + USERS_SERVICE_PORT + '/logout/'
        reply = requests.get(url,data=json.dumps({'user_di': user_id}), content_type='application/json')
        json_data = reply.json()
        return json_data['response']
    except Timeout:
        return None


def signup_support(firstname, lastname, email, year, month, day, password):
    try:
        url = 'http://' + USERS_SERVICE_IP + ':' + USERS_SERVICE_PORT + '/login'
        user = {
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "dateofbirth": {
                "year": year,
                "month": month,
                "day": day
            },
            "password": password
        }
        reply = requests.get(url, data=json.dumps(user), content_type='application/json')
        json_data = reply.json()
        return json_data['error']
    except Timeout:
        return None