python manage.py makemigrations && \
python manage.py migrate && \
python manage.py createadminuser && \
django-admin compilemessages && \
python manage.py runserver 8000
