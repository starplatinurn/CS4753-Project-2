FROM python:3.7-slim-buster

ENV FLASK_APP app.py

COPY . . 

RUN pip install -r requirements.txt

CMD ["flask","run","--host","0.0.0.0"]