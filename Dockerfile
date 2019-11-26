# https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
# debian docker: https://hub.docker.com/_/debian
FROM debian:latest

MAINTAINER Mauro Orrù <mauroorru3@gmail.com>
# RUN git clone dockerize -q https://github.com/SWE-AGGERS/stories_service.git

RUN apt-get update && apt-get install \
  -y --no-install-recommends python3 python3-setuptools python3-pip # git

# RUN git clone --single-branch --branch dockerize -q https://github.com/SWE-AGGERS/stories_service.git
# RUN git clone -q https://github.com/SWE-AGGERS/stories_service.git

ADD . /code
WORKDIR code

RUN python3 -m pip install -r requirements.txt

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV FLASK_APP service/app.py

EXPOSE 5000

# bind to 0.0.0.0 will make Docker works
CMD ["python3","-m","flask","run","--host", "0.0.0.0"]
