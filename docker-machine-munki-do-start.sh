#!/bin/bash

# Munki container variables
MUNKI_REPO="/Users/glgrp/src/munki_repo"
MUNKI_DO_DB="/Users/glgrp/src/munki-do-db"
# Comment this out to disable git
#GIT_PATH='/usr/bin/git'
# Comment this out to disable git branching (so all commits are done to master branch)
#GIT_BRANCHING='yes'
# Comment this out to enable git to track the 'pkgs' directory
#GIT_IGNORE_PKGS='yes'
MANIFEST_RESTRICTION_KEY='restriction'

# Gitlab
# Note: volume linking to /Users won't work in OS X due to a permissions issue, 
# so needs to be linked to a folder in the boot2docker host. You may wish to back
# this up in case you decide to destroy the docker-machine.
# Comment this out or set as '' if you don't want to build a Gitlab server
#GITLAB_DATA="/home/docker/gitlab-data"

# Check that Docker Machine exists
if [ -z "$(docker-machine ls | grep munkido)" ]; then
	docker-machine create -d vmwarefusion munkido --vmwarefusion-disk-size=10000000
	docker-machine env munkido
	eval "$(docker-machine env munkido)"
fi

# Check that Docker Machine is running
if [ "$(docker-machine status munkido)" != "Running" ]; then
	docker-machine start munkido
	docker-machine env munkido
	eval "$(docker-machine env munkido)"
fi

# Get the IP address of the machine
IP=`docker-machine ip munkido`

# Clean up
# This checks whether munki munki-do etc are running and stops them
# if so (thanks to Pepijn Bruienne):
docker ps -a | sed "s/\ \{2,\}/$(printf '\t')/g" | \
	awk -F"\t" '/munki|munki-do|gitlab|gitlab-postgresql|gitlab-redis/{print $1}' | \
	xargs docker rm -f
	
## GITLAB settings

if [ $GITLAB_DATA ]; then
	# Gitlab-postgres database
	# - comment out if you're using an external Git repository or not using Git
	docker run --name gitlab-postgresql -d \
		--env 'DB_NAME=gitlabhq_production' \
		--env 'DB_USER=gitlab' --env 'DB_PASS=password' \
		--volume $GITLAB_DATA/postgresql:/var/lib/postgresql \
		quay.io/sameersbn/postgresql

	# Gitlab Redis instance
	# - comment out if you're using an external Git repository or not using Git
	docker run --name gitlab-redis -d \
		--volume $GITLAB_DATA/redis:/var/lib/redis \
		quay.io/sameersbn/redis:latest

	# Gitlab
	# - comment out if you're using an external Git repository or not using Git
	docker run --name gitlab -d \
		--link gitlab-postgresql:postgresql --link gitlab-redis:redisio \
		--publish 10022:22 --publish 10080:80 \
		--env 'GITLAB_PORT=10080' --env 'GITLAB_SSH_PORT=10022' \
		--env 'GITLAB_SECRETS_DB_KEY_BASE=sxRfjpqHCfwMBHfrP8NXp5V6gS2wxBLXgv57pdvGKQMQSLTfDzBFfTf2vhQLvrxK' \
		--volume $GITLAB_DATA/gitlab:/home/git/data \
		quay.io/sameersbn/gitlab:8.1.0-2

	# Docker-gitlab - Since ssh-keyscan doesn't generate the
	# correct syntax, you need to copy the line directly from your OS X host's known_hosts file
	# into the `echo` statement. You must manually make a connection to the git repo in order
	# to generate the ssh key:
	cat ~/.ssh/known_hosts | grep $IP > docker/known_hosts

	# Note: after first run, you will need to set up your Gitlab repository. This involves:
	# # Logging in via a browser (http://IP-address:10080). 
	# # Default username (root) and password (5iveL!fe).
	# # Changing the password
	# # Logging in again with the new password
	# # Clicking +New Project
	# # Setting the project path to 'munki_repo'
	# # Select Visibility Level as Public
	# # Click Create Project
	# # If you haven't already created an ssh key, do so using the hints at http://IP-address:10080/help/ssh/README
	# # In Terminal, enter the command 'pbcopy < ~/.ssh/id_rsa.pub'
	# # If recreating a destroyed docker-machine, you need to remove the existing entry from
	# #   ~/.ssh/known_hosts
	# # If you aren't on master branch, `git checkout -b origin master`
	# # Push the branch you are on using `git push --set-upstream origin master`
fi
## END of GITLAB settings


# This isn't needed for Munki-Do to operate, but is needed if you want a working
# Munki server
docker run -d --restart=always --name="munki" -v $MUNKI_REPO:/munki_repo \
	-p 80:80 -h munki groob/docker-munki

# This is optional for complicated builds. It's essential if you're using gitlab in the docker-machine. 
docker build -t="grahampugh/munki-do" .


# munki-do container
docker run -d --restart=always --name munki-do \
	-p 8000:8000 \
	-v $MUNKI_REPO:/munki_repo \
	-v $MUNKI_DO_DB:/munki-do-db \
	-e DOCKER_MUNKIDO_GIT_PATH="$GIT_PATH" \
	-e DOCKER_MUNKIDO_GIT_BRANCHING="$GIT_BRANCHING" \
	-e DOCKER_MUNKIDO_GIT_IGNORE_PKGS="$GIT_IGNORE_PKGS" \
	-e DOCKER_MUNKIDO_MANIFEST_RESTRICTION_KEY="$MANIFEST_RESTRICTION_KEY" \
	-e ADMIN_PASS="pass" \
	grahampugh/munki-do


# Bitbucket / Github - use the following two lines to set up the entry in known_hosts:
# docker exec -it munki-do ssh-keygen -R bitbucket.org
# docker exec -it munki-do ssh-keyscan bitbucket.org > /root/.ssh/known_hosts


echo
echo "### Your Docker Machine IP is: $IP"
echo "### Your Munki-Do URL is: http://$IP:8000"
echo


