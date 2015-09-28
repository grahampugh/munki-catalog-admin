from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.conf import settings

from django.contrib.auth.models import User, Group
from guardian.shortcuts import get_objects_for_user

PROJECT_DIR = settings.PROJECT_DIR


def index(request):
	hanlde=open(PROJECT_DIR+"/../version", 'r+')
	version=hanlde.read()

