Munki-Do
--------------

Munki-Do enables the manipulation of Munki packages via the web. Munki-Do is 
an altered version of MunkiWebAdmin (v1) from Greg Neagle.  

* https://github.com/munki/munkiwebadmin

Some existing functionality from MunkiWebAdmin has been retained:

1. Manifests: create/delete manifests, and manage the contents of manifests.
2. Catalogs: view the contents of catalogs, view pkginfo file contents in tabular form. 

New functionality has been added:

1. Add multiple packages to a new or existing catalog
2. Remove multiple packages from a catalog
3. Move packages to a new or existing catalog
4. Delete packages and their associated pkginfo files
5. Download packages directly from the Munki Repo for ad-hoc installation

Some of the original functionality of MunkiWebAdmin has been removed from Munki-Do,
such as reporting tools. For reporting tools, I recommend: 

* *Sal:* https://github.com/salopensource/sal
* *MunkiReport-PHP:* https://github.com/munkireport/munkireport-php

Munki-Do was forked from Steve Kueng's forked development of MunkiWebAdmin: 

* https://github.com/SteveKueng/munkiwebadmin

The function to manipulate pkginfo files utilises munkitools (specifically, the 
`makecatalogs` command). This has been tested on an Ubuntu 14.04 VM, but you will 
need to ensure that your nginx user has write permissions to your munki repo. Use of group 
permissions is recommended. 

The code which enables movement of packages between catalogs is a derivation of code 
from Munki-Trello by Graham Gilbert: https://github.com/grahamgilbert/munki-trello

A Docker container for Munki-Do is available here: 

* https://github.com/grahampugh/docker-munki-catalog-admin

I've also made a Docker container for Steve Kueng's fork of MunkiWebAdmin, available here:

* https://github.com/grahampugh/docker-munkiwebadmin

*New!* Permissions are now working for the Packages view. You can now 
set users who can view but not edit Packages.

To Do
----

Munki-Do is still a work in progress, so shouldn't be used in production. 
I welcome the raising of issues, and pull requests..
