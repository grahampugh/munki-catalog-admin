#!/bin/bash

#Check that Docker Machine is running
if [ "$(docker-machine status default)" != "Running" ]; then
	docker-machine start default
	docker-machine env default
	eval "$(docker-machine env default)"
fi

# Pull
docker pull postgres

# Clean up
# This checks whether munki munki-do postgres-munkiwebadmin are running and stops them
# if so:
docker ps | sed "s/\ \{2,\}/$(printf '\t')/g" | \
   awk -F"\t" '/munki|munki-do|postgres-munkiwebadmin/{print $1}' | \
   xargs docker rm -f
# docker stop munki munki-do postgres-munkiwebadmin
# docker rm munki munki-do postgres-munkiwebadmin

# docker-machine ssh default -- sudo mkdir -p /munki_repo
# docker-machine ssh default -- df /munki_repo | grep -q /munki_repo && sudo umount /munki_repo || echo "munki_repo not mounted"
# docker-machine ssh default -- sudo mount -t vboxsf -o defaults,uid=$DOCKER_UID,gid=$DOCKER_GID $MUNKI_REPO /munki_repo
    
# Run
# chmod -R 777 /usr/local/docker/nbi
IP=`docker-machine ip default`
echo "IP = $IP"

# Munki container
MUNKI_REPO="/Users/glgrp/src/munki_repo"

docker run -d --restart=always --name="munki" -v $MUNKI_REPO:/munki_repo \
   -p 80:80 -h munki groob/docker-munki

# Postgres container for Munkiwebadmin
docker run -d --restart=always \
   --name="postgres-munkiwebadmin" postgres

# Database setup:
#./setup_db.sh

# You could substitute this for git clone to a temprary folder. 
# Make sure you delete the folder after running the container.
#cd /path/to/docker-munki-do && \
docker build -t="grahampugh/munki-do" .

# munki-do container
docker run -d --restart=always --name munki-do \
   -p 8000:8000 \
   --link postgres-munkiwebadmin:db \
   -v $MUNKI_REPO:/munki_repo \
   -e ADMIN_PASS=pass \
   -e DB_NAME=munkiwebadmin \
   -e DB_USER=admin \
   -e DB_PASS=password \
   grahampugh/munki-do

