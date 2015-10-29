#!/usr/bin/python
from os import getenv
import locale
from system_settings import *


# Read the list of allowed hosts from the $DOCKER_MUNKIDO_ALLOWED_HOSTS env var, or
# allow all hosts if none was set.
if getenv('DOCKER_MUNKIDO_ALLOWED_HOSTS'):
    ALLOWED_HOSTS = getenv('DOCKER_MUNKIDO_ALLOWED_HOSTS').split(',')
else:
    ALLOWED_HOSTS = ['*']


# Read list of admins from $DOCKER_MUNKIDO_ADMINS env var
admin_list = []
if getenv('DOCKER_MUNKIDO_ADMINS'):
    admins_var = getenv('DOCKER_MUNKIDO_ADMINS')
    if ',' in admins_var and ':' in admins_var:
        for admin in admins_var.split(':'):
            admin_list.append(tuple(admin.split(',')))
        ADMINS = tuple(admin_list)
    elif ',' in admins_var:
        admin_list.append(tuple(admins_var.split(',')))
        ADMINS = tuple(admin_list)
else:
    ADMINS = (
                ('Admin User', 'admin@test.com')
             )


# Read the preferred time zone from $DOCKER_SAL_TZ, use system locale or
# set to 'America/New_York' if neither are set
if getenv('DOCKER_MUNKIDO_TZ'):
    if '/' in getenv('DOCKER_MUNKIDO_TZ'):
        TIME_ZONE = getenv('DOCKER_MUNKIDO_TZ')
    else: TIME_ZONE = 'America/New_York'
# elif getenv('TZ'):
#     TIME_ZONE = getenv('TZ')
# else:
#     TIME_ZONE = 'America/New_York'


# Read the default start URL from $DOCKER_MUNKIDO_LOGIN_REDIRECT_URL env var, or
# set to '/catalog' as default
if getenv('DOCKER_MUNKIDO_LOGIN_REDIRECT_URL'):
    LOGIN_REDIRECT_URL = getenv('DOCKER_MUNKIDO_LOGIN_REDIRECT_URL')
else:
    LOGIN_REDIRECT_URL='/catalog'


# Read the $DOCKER_MUNKIDO_ALL_ITEMS env var, or
# set to False as default
# if true all software packages are shown in autocompletion not only the one in included catalogs
if getenv('DOCKER_MUNKIDO_ALL_ITEMS'):
    ALL_ITEMS = getenv('DOCKER_MUNKIDO_ALL_ITEMS')
else:
    ALL_ITEMS=False


# Read the path to git from the $DOCKER_MUNKIDO_GIT_PATH env var, or
# specify an empty git path, which disables git
if getenv('DOCKER_MUNKIDO_GIT_PATH'):
    GIT_PATH = getenv('DOCKER_MUNKIDO_GIT_PATH')
else:
    GIT_PATH = ''


# Read the $DOCKER_MUNKIDO_GIT_IGNORE_PKGS env var, or
# specify an empty string, which means the pkgs folder is *not* ignored
if getenv('DOCKER_MUNKIDO_GIT_IGNORE_PKGS'):
    GIT_IGNORE_PKGS = getenv('DOCKER_MUNKIDO_GIT_IGNORE_PKGS')
else:
    GIT_IGNORE_PKGS = ''


# Read the $DOCKER_MUNKIDO_GIT_BRANCHING env var, or
# specify an empty string, which means git branching is *not* enabled
if getenv('DOCKER_MUNKIDO_GIT_BRANCHING'):
    GIT_BRANCHING = getenv('DOCKER_MUNKIDO_GIT_BRANCHING')
else:
    GIT_BRANCHING = ''


# Read the $DOCKER_MUNKIDO_PRODUCTION_BRANCH env var, or
# specify 'master' as default
if getenv('DOCKER_MUNKIDO_PRODUCTION_BRANCH'):
    PRODUCTION_BRANCH = getenv('DOCKER_MUNKIDO_PRODUCTION_BRANCH')
else:
    PRODUCTION_BRANCH = 'master'


# Read the $DOCKER_MUNKIDO_MANIFEST_USERNAME_KEY env var, or
# specify 'user' as default (this is not yet enabled)
if getenv('DOCKER_MUNKIDO_MANIFEST_USERNAME_KEY'):
    MANIFEST_USERNAME_KEY = getenv('DOCKER_MUNKIDO_MANIFEST_USERNAME_KEY')
else:
    MANIFEST_USERNAME_KEY = 'user'

# Read the $DOCKER_MUNKIDO_MANIFEST_RESTRICTION_KEY env var, or
# specify '' as default (which disables manifest restriction)
# To enable, set as 'restriction'
if getenv('DOCKER_MUNKIDO_MANIFEST_RESTRICTION_KEY'):
    MANIFEST_RESTRICTION_KEY = getenv('DOCKER_MUNKIDO_MANIFEST_RESTRICTION_KEY')
else:
    MANIFEST_RESTRICTION_KEY = ''


# Read the $DOCKER_MUNKIDO_MANIFEST_USERNAME_IS_EDITABLE env var, or
# specify False as default (user editing is not yet enabled anyway)
if getenv('DOCKER_MUNKIDO_MANIFEST_USERNAME_IS_EDITABLE'):
    MANIFEST_USERNAME_IS_EDITABLE = getenv('DOCKER_MUNKIDO_MANIFEST_USERNAME_IS_EDITABLE')
else:
    MANIFEST_USERNAME_IS_EDITABLE = False

