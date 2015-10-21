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

Munki-Do is now enabled for Git. If you set the `GIT_PATH` path in `settings.py`, 
any changes made to the manifests or pkginfo files will attempt to be committed to 
the git repository.  By default, these are committed to the current branch, which is not 
determined by Munki-Do. See Git Branching below to change this behaviour.

To enable git in your repository, follow the instructions here: 
https://github.com/munki/munki/wiki/Munki-With-Git

You can put the `pkgs` folder in `.gitignore`, but you must allow the `catalogs`, 
`manifests` and `pkgsinfo` folders to be updated.

Munki-Do does not determine the branch of your repository, so you could choose to 
work on an "unstable" branch and use another means to push to a master branch (e.g. 
manual intervention by a superuser, or a cron job).

# Git Branching

Git branching is now available. This is enabled in 
`settings.py` by setting `GIT_BRANCHING` to 'yes'.

With Git branching enabled, any commit made by a user creates a new branch 
in the repo named `username_DDMMYYhhmmss` and pushes the changes to that branch. 
The server then checks out the default branch to maintain a consistent view for 
all users and avoid checkout competition.

Note: no commit notification is built into Munki-Do. You should configure your Git 
repository to provide notifications when new commits are pushed.  I recommend using 
Slack for these notifications.

An administrator with rights to the repo then can check and merge (or reject) the user's 
branch into the master branch.

A button is made available for users to update their view (this issues a 'git pull' 
command).

The `GIT_IGNORE_PKGS` key in `settings.py` allows you to ignore the `pkgs` directory, 
in the case that you have set git to ignore this folder. This is a common scenario due to 
the large file sizes stored in the pkgs folder.

If `GIT_IGNORE_PKGS` is enabled, Munki-Do will simply delete the files in the `pkgs` 
folder, rather than using `git rm` and committing the changes to a git repository.

If both `GIT_IGNORE_PKGS` and `GIT_BRANCHING` are enabled, then since changes are made 
to a new git branch and are not "live" on the production branch, 
it is important that the contents of the `pkgs` folder are not 
deleted at the time of commit. The act of deleting contents 
from the `pkgs` folder then becomes manual, to be 
done by the administrator performing git merges.  To facilitate this, use the 
_"Manage Orphaned Packages"_ link, which lists all files in the `pkgs` folder which are 
not referenced in a `pkginfo` file (and which are therefore irrelevant to the munki 
repository). These packages can then be selected and deleted using the UI. At present 
this link is only available to users that are marked as "Staff" in the admin panel.

To Do
----

Munki-Do is still a work in progress, so use in production at your own risk. 
I welcome the raising of issues, and pull requests...

Possible new features:

  * Restrict user access to specific Manifests
  * Reskin to MunkiWebAdmin 2 UI when it's released. 
  * (or, alternatively, reskin the Packages section to take advantage of SteveKueng's UI)
  * Inline XML editor for editing pkginfo files, e.g. CKEditor
  * Icon handling (deleting orphaned icons)
