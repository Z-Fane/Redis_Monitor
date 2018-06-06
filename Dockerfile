FROM python:3.6-alpine

RUN adduser -D zfane

WORKDIR /home/zfane

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn pymysql flask-sqlalchemy

COPY app app
COPY manager.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP manager.py

RUN chown -R zfane:zfane ./
USER zfane

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]