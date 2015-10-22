docker-munki-do
===============

This Docker container runs [Munki-Do](https://github.com/grahampugh/munki-do), which is a fork of MunkiWebAdmin.
Several options, such as the timezone and admin password are customizable using environment variables.

#Docker Machine
If you're running Docker Machine, you can simply clone this repo and run a startup script. Note you'll probably want to change the `MUNKI_REPO` path in `docker-machine-munki-do-start.sh`:
```bash
$ git clone https://github.com/grahampugh/docker-munki-do.git
$ cd docker-munki-do
$ ./docker-machine-munki-do-start.sh
```

#Postgres container
You must run the PostgreSQL container before running the munki-do container.
Currently there is support only for PostgreSQL.
I use the [stackbrew postgres container](https://registry.hub.docker.com/_/postgres/) from the Docker Hub, but you can use your own. The app container expects the following environment variables to connect to a database:
```
DB_NAME
DB_USER
DB_PASS
```

See [this blog post](http://davidamick.wordpress.com/2014/07/19/docker-postgresql-workflow/) for an example for an example workflow using the postgres container.
The `setup_db.sh` script in the GitHub repo will create the database tables for you.
The official guide on [linking containers](https://docs.docker.com/userguide/dockerlinks/) is also very helpful.

```bash
$ docker pull postgres
$ docker run --name="postgres-munkiwebadmin" -d postgres
```
Edit the `setup.db` script from the github repo to change the database name, user and password before running it.
```bash
$ ./setup_db.sh
```

#Image Creation
```$ docker build -t="grahampugh/munki-do" .```
or
```$ make```

#Running the Munki-Catalog-Admin Container

```bash
$ docker run -d --name="munki-do" \
  -p 8000:8000 \
  --link postgres-munkiwebadmin:db \
  -v /tmp/munki_repo:/munki_repo \
  -e ADMIN_PASS=pass \
  -e DB_NAME=munkiwebadmin \
  -e DB_USER=admin \
  -e DB_PASS=password \
  grahampugh/munki-do
```
or
```bash
$ make run
```
This assumes your Munki repo is mounted at /tmp/munki_repo.

#Using with a Munki Repo that uses Git

Munki-Do is now able to update your Git-enabled Munki Repo. This container does not
clone the repo internally - it links to a Munki Container, so that Munki-Do
operates on the production Repository. Nevertheless, it maintains your Git repo to which
it is linked. 

You could choose to link to a container that was an "unstable" branch of your Munki Repo,
and manually merge to the master by some other means (manual intervention, or a nightly
`cron` job, for instance).

To enable Git operations, set the path to `git` (`GIT_PATH`) in `settings.py`. 
Unless you change the base container, the path is `/usr/bin/git`.
*(TO DO - enable this as a flag in the Docker run command)*

To use an SSH key (required for password-protected Git repositories): 
  * generate an SSH key (`id-rsa` file) as per the instructions [here](https://confluence.atlassian.com/bitbucket/set-up-ssh-for-git-728138079.html) 
  * copy the `id_rsa` file into the same folder as the Dockerfile
  * unhash the relevant lines in the `Dockerfile` to copy the file into the container
