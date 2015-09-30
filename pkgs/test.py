#from django.db import models
import os
import sys
import subprocess
import plistlib
import optparse
import fnmatch

root = "/Volumes/Images/vagrant/docker-munki/munki_repo/pkgsinfo/apps"
name = "Slack-1.1.3.plist"
pkg_catalog = "production"

done = False
try:
	plist = plistlib.readPlist(os.path.join(root, name))
except:
	pass
# Check that the catalog is not already in this plist
if pkg_catalog not in plist['catalogs']:
	plist['catalogs'].append(pkg_catalog)
	plistlib.writePlist(plist, os.path.join(root, name))
done = True
