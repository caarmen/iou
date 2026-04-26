FROM python:3.12.0-slim

RUN apt-get update && apt-get install -y gettext

WORKDIR /app

COPY iouproject ./iouproject
COPY iou ./iou
COPY passkeys ./passkeys
COPY requirements/prod.txt requirements.txt
COPY manage.py ./


RUN pip install -r requirements.txt

ENV DEBUG false

CMD python manage.py migrate && \
    python manage.py createadminuser && \
    django-admin compilemessages && \
    python manage.py collectstatic --clear --no-input && \
    gunicorn --bind 0.0.0.0:8000 iouproject.wsgi
