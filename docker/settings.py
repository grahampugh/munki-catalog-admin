# Django settings for munki-do project.
from django.conf import global_settings
from system_settings import *
from settings_import import ADMINS, TIME_ZONE, ALLOWED_HOSTS, GIT_PATH, GIT_IGNORE_PKGS, GIT_BRANCHING, PRODUCTION_BRANCH, MANIFEST_USERNAME_KEY, MANIFEST_USERNAME_IS_EDITABLE, MANIFEST_RESTRICTION_KEY, LOGIN_REDIRECT_URL, ALL_ITEMS

# Override native makecatalogs with docker-installed path
DEFAULT_MAKECATALOGS='/munki-tools/code/client/makecatalogs'

# MUNKI_REPO_DIR holds the local filesystem path to the Munki repo
MUNKI_REPO_DIR = '/munki_repo'

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

