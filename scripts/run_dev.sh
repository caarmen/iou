export DEBUG=true
python manage.py migrate && \
python manage.py createadminuser && \
pushd iou && django-admin makemessages --locale en_US --locale fr && popd && \
django-admin compilemessages && \
python manage.py runserver 8000
