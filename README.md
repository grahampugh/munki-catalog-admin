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
4. Delete packages and their associated `pkginfo` files
5. Delete orphaned packages (those without corresponding `pkginfo` files)
6. Download packages directly from the Munki Repo for ad-hoc installation
7. Works with git-enabled Munki repositories
8. Can be set to create new git branches for each update, based on logged in user.

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

This git repository contains all the necessary files to run a Docker container.
The following environment variables can be set in a `docker run` command:

  * `DOCKER_MUNKIDO_TZ` - timezone - `America/New_York` by default
  * `DOCKER_MUNKIDO_LOGIN_REDIRECT_URL` - determines the first page shown after login.
     Default is `/catalog`. Valid options are `/catalog`, `/manifest`, `/pkg`. You may
     wish to change this if disabling access to some features for certain users.
  * `ADMIN_PASS` - default admin user password.
  * `DOCKER_MUNKIDO_ALL_ITEMS` - if `True`, when editing manifests, all software packages 
     are shown in autocompletion, not only the one in included catalogs. Default is 
     `False`
  * `DOCKER_MUNKIDO_PRODUCTION_BRANCH` - the default Git branch -  default is "master"
  * `DOCKER_MUNKIDO_GIT_PATH` - See "Munki-with-Git" below
  * `DOCKER_MUNKIDO_GIT_BRANCHING` - See "Git Branching" below
  * `DOCKER_MUNKIDO_GIT_IGNORE_PKGS` - See "Munki-with-Git" below
  * `DOCKER_MUNKIDO_MANIFEST_RESTRICTION_KEY` - See "Restricting manifest editing rights" 
     below.

Example:
```bash
docker run -d --restart=always --name munki-do \
    -p 8000:8000 \
    -v /var/www/html/munki_repo:/munki_repo \
    -v /home/myhome/munki-do-db:/munki-do-db \
    -e DOCKER_MUNKIDO_GIT_PATH="/usr/bin/git" \
    -e DOCKER_MUNKIDO_GIT_BRANCHING="yes" \
    -e DOCKER_MUNKIDO_GIT_IGNORE_PKGS="yes" \
    -e DOCKER_MUNKIDO_MANIFEST_RESTRICTION_KEY="restriction" \
    -e ADMIN_PASS="pass" \
    grahampugh/munki-do
```

You must set up a directory on your local host for the Django database. This is 
specified in your `docker run` command as in the above example.


#Quick setup
`docker-machine-munki-do-start.sh` is a single shell script designed to get 
Munki-Do running in a test environment. You need to have Docker Toolbox installed to 
use this, and you will need to edit the paths to your `munki_repo` and 
`munki-do-db` directories. 

Set `$MUNKI_DO_DB` to a directory on your host system in 
`docker-machine-munki-do-start.sh` for the Django database.

If you set the `GITLAB_DATA` variable in `docker-machine-munki-do-start.sh`, 
Gitlab is setup on the resulting Docker Machine,
so you can test Munki-Do's Git capabilities on a local git repository. Note that if you
choose to do this, you must set up the `munki_repo` repository in the Gitlab UI:

  * Log in via a browser (http://IP-address:10080) 
  * Default username (root) and password (5iveL!fe)
  * Change the password
  * Log in again with the new password
  * Click "+New Project"
  * Setting the project path to "munki_repo"
  * Select Visibility Level as Public
  * Click Create Project
  * If you haven't already created an ssh key, do so using the hints at 
    http://IP-address:10080/help/ssh/README
  * In Terminal on your host Mac system, enter the command `pbcopy < ~/.ssh/id_rsa.pub`
  * Paste the value into a new Key in the Gitlab UI. 
  * If recreating a destroyed docker-machine, you need to remove the existing entry from
    `~/.ssh/known_hosts`
  * If you aren't on master branch: `git checkout -b origin master`
  * Push the branch you are on: `git push --set-upstream origin master`



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

#Restricting manifest editing rights

You may wish to restrict the right to edit certain manifests to certain users in your organisation.
For example, you may wish to allow the editing of individual client manifests, but prevent
editing of certain "core" manifests that affect a large number of machines. Alternatively,
you may have different manifests for different organisational units, and may wish to 
only allow members of those units to edit their own manifests.

Munki-Do can be configured to restrict manifest editing based on Django group membership.
To enable this feature, set `MANIFEST_RESTRICTION_KEY` in `settings.py` or with the Docker
`DOCKER_MUNKIDO_MANIFEST_RESTRICTION_KEY` environment variable. Normally, "restriction"
will suffice.

Any group created in Munki-Do's Django admin interface can be used, as can 'staff' and 
'superuser'. If you enter a group name which doesn't exist, only superusers will be able to
edit that manifest. Superusers can edit any manifest.

#Munki-with-Git

Munki-Do is now enabled for Git. If you set the `GIT_PATH` path in `settings.py` or with
the `DOCKER_MUNKIDO_GIT_PATH` Docker environment variable, 
any changes made to the manifests or pkginfo files will attempt to be committed to 
the git repository.  By default, these are committed to the current branch, which is not 
determined by Munki-Do. See Git Branching below to change this behaviour.

To enable git in your repository, follow the instructions here: 
https://github.com/munki/munki/wiki/Munki-With-Git

You can put the `pkgs` folder in `.gitignore`, but you must allow the `catalogs`, 
`manifests` and `pkgsinfo` folders to be updated.

The `GIT_IGNORE_PKGS` key in `settings.py` or the `DOCKER_MUNKIDO_GIT_IGNORE_PKGS` Docker 
environment variable allows you to ignore the `pkgs` directory, 
in the case that you have set git to ignore this folder. This is a common scenario due to 
the large file sizes stored in the pkgs folder.

If `GIT_IGNORE_PKGS` is enabled, Munki-Do will simply delete the files in the `pkgs` 
folder, rather than using `git rm` and committing the changes to a git repository.

# Git Branching

Git branching is now available. This is enabled in 
`settings.py` by setting `GIT_BRANCHING` to 'yes' (or with the 
`DOCKER_MUNKIDO_GIT_BRANCHING` Docker environment variable.

By default, Munki-Do does not determine the branch of your repository. You could choose to 
work on an "unstable" branch and use another means to push to a master branch (e.g. 
manual intervention by a superuser, or a cron job).

With Git branching enabled, any commit made by a user creates a new branch 
in the repo named `username_DDMMYYhhmmss` and pushes the changes to that branch. 
The server then checks out the default branch (normally 'master') to maintain a consistent view for 
all users and avoid checkout competition.

Note: no commit notification is built into Munki-Do. You should configure your Git 
repository to provide notifications when new commits are pushed.  I recommend using 
Slack for these notifications.

An administrator with rights to the repo then can check and merge (or reject) the user's 
branch into the master branch.

A button is made available for users to update their view (this issues a 'git pull' 
command).

When a new manifest is created, pushing to git is delayed until a change is made to 
that manifest. This avoids the Munki-Do user's view returning to the master branch,
which doesn't yet contain the new manifest. The active branch in the server remains 
set to the newly created branch until the new manifest is edited and saved, at which time 
it is committed to the new branch and the master branch is checked out.

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

  * Reskin to MunkiWebAdmin 2 UI when it's released. 
  * (or, alternatively, reskin the Packages section to take advantage of SteveKueng's UI)
  * Inline XML editor for editing pkginfo files, e.g. CKEditor
  * Icon handling (deleting orphaned icons)
  * Sort out docker environment variables so Munki-Do can be run straight from Dockerhub
