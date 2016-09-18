import os
import socket
import logging
from django.conf import global_settings

##############################
# Munki-Do-specific settings #
##############################

# APPNAME is user-visable web app name
APPNAME = 'Munki-Do'
# MUNKI_REPO_DIR holds the local filesystem path to the Munki repo
MUNKI_REPO_DIR = '/munki_repo'
ICONS_DIR = 'icons'
PKGS_DIR = 'pkgs'

## GIT STUFF ##
# provide the path to the git binary if you want MunkiWeb to add and commit
# manifest edits to a git repo
# if GIT_PATH is undefined or None MunkiWeb will not attempt to do a git add
# or commit
GIT_PATH = ''
#GIT_PATH = '/usr/bin/git'
# If GIT_IGNORE_PKGS is empty, git will attempt to remove packages.
# Otherwise, the packages will be deleted as standard.
GIT_IGNORE_PKGS = 'yes'
# If GIT_BRANCHING is enabled, users create a new branch when making a commit
# (if that branch doesn't already exist) rather than committing to the 
# current branch)
#GIT_BRANCHING = 'yes'
GIT_BRANCHING = ''
# If Git branching is available, you should set the default branch here.
# This is the branch which people logging into Munki-Dp will see.
# This may be master, or something else if you have a different workflow.
PRODUCTION_BRANCH = 'master'
## END OF GIT STUFF ##

# The following is used for the download links for pkgs.
# It assumes that the full munki_repo is accessable at /munki_repo
MUNKI_PKG_ROOT = os.path.join(MUNKI_REPO_DIR, PKGS_DIR)

# name of the key in a manifest file that names the user or dept
MANIFEST_USERNAME_KEY = 'user'
# set MANIFEST_USERNAME_IS_EDITABLE to allow edits to the displayed username
MANIFEST_USERNAME_IS_EDITABLE = True

# path to makecatalogs - required for packages section
#DEFAULT_MAKECATALOGS = "/usr/local/munki/makecatalogs"
DEFAULT_MAKECATALOGS = "/munki-tools/code/client/makecatalogs"

#if true all software packages are shown in autocompletion not only the one in included catalogs
ALL_ITEMS = True

# enable Business units
BUSINESS_UNITS_ENABLED = False

# needed for productive mode
ALLOWED_HOSTS = ['*']

TOKEN_TIMEOUT_DAYS = 1

ANONYMOUS_USER_ID = -1

# -------------------------

USE_LDAP = False
# LDAP authentication support
if USE_LDAP:
    import ldap
    from django_auth_ldap.config import LDAPSearch, PosixGroupType
    
    # LDAP settings
    AUTH_LDAP_SERVER_URI = "ldap://foo.example.com"
    AUTH_LDAP_BIND_DN = ""
    AUTH_LDAP_BIND_PASSWORD = ""
    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        "ou=People,o=ExampleCorp,c=US",
        ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
    AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
        "ou=Groups,o=ExampleCorp,c=US",
        ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)")
    AUTH_LDAP_GROUP_TYPE = PosixGroupType()
    AUTH_LDAP_FIND_GROUP_PERMS = True
    AUTH_LDAP_USER_ATTR_MAP = {"first_name": "givenName", 
                               "last_name": "sn",
                               "email": "mail"}
    # Cache group memberships for an hour to minimize LDAP traffic
    AUTH_LDAP_CACHE_GROUPS = True
    AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Admin', 'admin@mydomain.com'),
)

MANAGERS = ADMINS

# using sqlite3
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '/munki-do-db/munki-do.db',                      # Path to database file if using sqlite3.
        'USER': '',     # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}

# mysql example
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.mysql', 
#        'NAME': 'munkiweb',
#        'USER': 'munkiwebuser',
#        'PASSWORD': 'munkiwebuserpasswd',
#        'HOST': 'munkiwebdb.example.org',
#        'PORT': '',
#    }
#}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Zurich'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-US'

# -----------------

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

MEDIA_ROOT = os.path.join(MUNKI_REPO_DIR, ICONS_DIR)

MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'site_static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'x@hgx4r!1rm@c4lax96tx88*d1v+m$&)w1ur4-xvcqj(8as_$q'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    "munkido.processor.index",
    "django.core.context_processors.request",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

if USE_LDAP:
    AUTHENTICATION_BACKENDS = (
        'django_auth_ldap.backend.LDAPBackend',
        'django.contrib.auth.backends.ModelBackend',
        'tokenapi.backends.TokenBackend',
    )
else:
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'tokenapi.backends.TokenBackend',
    )

LOGIN_URL='/login/'
LOGIN_REDIRECT_URL='/catalogs'

ROOT_URLCONF = 'munkido.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'munkido',
    'tokenapi',
    'catalogs',
    'manifests',
    'pkgs',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
             'filename': '/var/log/django/error.log',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
             'filename': '/var/log/django/debug.log',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': '/var/log/django/info.log',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format':
                '%(levelname)s %(message)s'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'DEBUG',
        },
        'manifests.models': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'pkgs.models': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}
