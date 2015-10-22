#!/bin/bash

# Munki container
MUNKI_REPO="/Users/glgrp/src/munki_repo"
MUNKI_DO_DB="/Users/glgrp/src/munki-do-db"

#Check that Docker Machine exists
if [ -z "$(docker-machine ls | grep munkido)" ]; then
	docker-machine create -d vmwarefusion munkido --vmwarefusion-disk-size=10000000
	docker-machine env munkido
	eval "$(docker-machine env munkido)"
fi

#Check that Docker Machine is running
if [ "$(docker-machine status munkido)" != "Running" ]; then
	docker-machine start munkido
	docker-machine env munkido
	eval "$(docker-machine env munkido)"
fi


# Clean up
# This checks whether munki munki-do postgres-munkiwebadmin are running and stops them
# if so:
docker ps | sed "s/\ \{2,\}/$(printf '\t')/g" | \
	awk -F"\t" '/munki|munki-do/{print $1}' | \
	xargs docker rm -f

docker run -d --restart=always --name="munki" -v $MUNKI_REPO:/munki_repo \
	-p 80:80 -h munki groob/docker-munki

# You could substitute this for git clone to a temprary folder. 
# Make sure you delete the folder after running the container.
#cd /path/to/docker-munki-do && \
docker build -t="grahampugh/munki-do" .

# munki-do container
docker run -d --restart=always --name munki-do \
	-p 8000:8000 \
	-v $MUNKI_REPO:/munki_repo \
	-v $MUNKI_DO_DB:/munki-do-db \
	-e ADMIN_PASS=pass \
	grahampugh/munki-do

# Run
IP=`docker-machine ip munkido`
echo
echo "### Your Docker Machine IP is: $IP ###"
echo "### Your Munki-Do URL is: http://$IP:8000"
echo


