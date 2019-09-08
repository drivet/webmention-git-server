FROM python:3.6-slim

RUN apt-get update && \
    apt-get -y install build-essential && \
    pip install uwsgi && \
    apt-get purge -y build-essential && \
    apt -y autoremove

WORKDIR /app

ADD . /app

ENV WEBMENTION_ROOT /var/local/webmention

RUN pip install -r requirements-prod.txt

CMD ["uwsgi", "app.ini"]
