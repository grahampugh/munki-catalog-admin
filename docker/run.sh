#!/bin/bash

cd $APP_DIR
ADMIN_PASS=${ADMIN_PASS:-}
python manage.py syncdb
python manage.py makemigrations
python manage.py migrate

echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'docker@localhost', 'password')" | python manage.py shell

python manage.py collectstatic --noinput

python manage.py runserver 0.0.0.0:8000