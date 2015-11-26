DOCKER_USER=grahamrpugh
NAME=munki-do
MUNKI_REPO="/Users/Shared/munki_repo"
MWA_PORT=8000
DB_CONTAINER_NAME="/Users/Shared/munki-do-db"
GIT_PATH=''
GIT_IGNORE_PKGS=''
GIT_BRANCHING=''
MANIFEST_RESTRICTION_KEY=''
DOCKER_RUN_COMMON=--name munki-do -p ${MWA_PORT}:8000 -v ${MUNKI_REPO{:/munki_repo -v ${DB_CONTAINER_NAME}:/munki-do-db -e DOCKER_MUNKIDO_GIT_PATH="${GIT_PATH}" -e DOCKER_MUNKIDO_GIT_BRANCHING="${GIT_BRANCHING}" -e DOCKER_MUNKIDO_GIT_IGNORE_PKGS="${GIT_IGNORE_PKGS}" -e DOCKER_MUNKIDO_MANIFEST_RESTRICTION_KEY="{$MANIFEST_RESTRICTION_KEY}" ${DOCKER_USER}/${NAME}

all: build

build:
	docker build -t="${DOCKER_USER}/${NAME}" .

run:
#	mkdir -p ${MUNKI_REPO_DIR}
	docker run -d --restart=always ${DOCKER_RUN_COMMON}

clean:
	docker stop $(NAME)
	docker rm $(NAME)
	
bash:
	docker exec -t -i $(NAME) /bin/bash

