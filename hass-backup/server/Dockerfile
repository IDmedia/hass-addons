FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY /app/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

VOLUME ["/app"]