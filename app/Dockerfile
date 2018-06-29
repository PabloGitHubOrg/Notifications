FROM tiangolo/uwsgi-nginx-flask:python3.6

ENV FLASK_APP=main.py
ENV FLASK_DEBUG=1

ADD requirements.txt /
RUN pip install -r /requirements.txt

COPY . /app

CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
