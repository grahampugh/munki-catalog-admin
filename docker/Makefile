DOCKER_USER=grahamrpugh
ADMIN_PASS=pass
MUNKI_REPO="/Users/glgrp/src/munki_repo"
MWA_PORT=8000
DB_NAME=munkiwebadmin
DB_PASS=password
DB_USER=admin
DB_CONTAINER_NAME:=postgres-munkiwebadmin
NAME:=munki-do
DOCKER_RUN_COMMON=--name="$(NAME)" -p ${MWA_PORT}:8000 --link $(DB_CONTAINER_NAME):db -v ${MUNKI_REPO}:/munki_repo -e ADMIN_PASS=${ADMIN_PASS} -e DB_NAME=$(DB_NAME) -e DB_USER=$(DB_USER) -e DB_PASS=$(DB_PASS) ${DOCKER_USER}/${NAME}
#DOCKER_RUN_COMMON=--name="$(NAME)" -p ${MWA_PORT}:8000 --link $(DB_CONTAINER_NAME):db -e ADMIN_PASS=${ADMIN_PASS} -e DB_NAME=$(DB_NAME) -e DB_USER=$(DB_USER) -e DB_PASS=$(DB_PASS) ${DOCKER_USER}/${NAME}


all: build

build:
	docker build -t="${DOCKER_USER}/${NAME}" .

run:
#	mkdir -p ${MUNKI_REPO_DIR}
	docker run -d ${DOCKER_RUN_COMMON}

clean:
	docker stop $(NAME)
	docker rm $(NAME)
	
bash:
	docker exec -t -i $(NAME) /bin/bash

