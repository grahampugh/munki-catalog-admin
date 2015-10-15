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

#Docker

I encourage the use of Munki-Do as a Docker container. I have personally never 
attempted to install it natively.

A Docker container for Munki-Do is available here: 

* https://github.com/grahampugh/docker-munki-do

I've also made a Docker container for Steve Kueng's fork of MunkiWebAdmin, available here:

* https://github.com/grahampugh/docker-munkiwebadmin

#User permissions

The Admin console can be used to set users with discrete permissions on the Packages,
Catalogs and Manifests sections. The relevant permissions are:

| User permission | What it allows |
| --- | --- |
| catalogs \| catalogs \| Can view catalogs | Viewing Catalogs Index - this *must* be set for all users |
| manifests \| manifests \| Can view manifests | Viewing Manifests Index - this *must* be set for all users |
| manifests \| manifests \| Can add manifests | Add new manifests |
| manifests \| manifests \| Can change manifests | Edit manifests |
| manifests \| manifests \| Can delete manifests | Delete manifests |
| pkgs \| pkgs \| Can view packages | Viewing Packages Index - this *must* be set for all users |
| pkgs \| pkgs \| Can change pkgs | Edit pkginfo files - i.e. add/remove catalog array entries |
| pkgs \| pkgs \| Can delete pkgs | Delete pkginfo files and packages from the repository |

Superusers automatically have all permissions. 
Users given 'staff' rights can access the admin console.

#Munki-with-Git

Munki-Do is now enabled for Git. If you set the path to `git` in `settings.py`, 
any changes made to the manifests or pkginfo files will attempt to be committed to 
the git repository.

To enable git in your repository, follow the instructions here: 
https://github.com/munki/munki/wiki/Munki-With-Git

You can put the `pkgs` folder in `.gitignore`, but you must allow the `catalogs`, 
`manifests` and `pkgsinfo` folders to be updated.

Munki-Do does not determine the branch of your repository, so you could choose to 
work on an "unstable" branch and use another means to push to a master branch (e.g. 
manual intervention by a superuser, or a cron job).

A future release may checkout a new branch based on the username, which can be viewed 
and managed by a superuser for merging. But not yet.

To Do
----

Munki-Do is still a work in progress, so use in production at your own risk. 
I welcome the raising of issues, and pull requests...

Git branching?
