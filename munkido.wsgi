import os, sys
import site

MUNKIDO_ENV_DIR = '/var/www/html/munkido'

# Use site to load the site-packages directory of our virtualenv
site.addsitedir(os.path.join(MUNKIDO_ENV_DIR, 'lib/python2.7/site-packages'))

# Make sure we have the virtualenv and the Django app itself added to our path
sys.path.append(MUNKIDO_ENV_DIR)
sys.path.append(os.path.join(MUNKIDO_ENV_DIR, 'munkido'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'munkido.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()