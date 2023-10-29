export DEBUG=false
python manage.py migrate && \
python manage.py createadminuser && \
django-admin compilemessages && \
python manage.py collectstatic --clear --no-input && \
gunicorn iouproject.wsgi
