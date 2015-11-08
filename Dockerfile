# This Dockerfile is specifically for placement in the Munki-Do git repo.
# A separate Dockerfile in the Docker-Munki-Do repo achieves the same build by cloning
# this repository.

# Use phusion/passenger-full as base image. To make your builds reproducible, make
# sure you lock down to a specific version, not to `latest`!
# See https://github.com/phusion/passenger-docker/blob/master/Changelog.md for
# a list of version numbers.
FROM phusion/passenger-full:0.9.17
MAINTAINER Graham Pugh <g.r.pugh@gmail.com>

# Set correct environment variables.
ENV HOME /root
ENV DEBIAN_FRONTEND noninteractive
ENV APP_DIR /home/docker/munkido
ENV APPNAME Munki-Do
ENV DOCKER_MUNKIDO_TZ America/New_York
# If GIT path is specified, git is enabled in Munki Do. 
# Provide an empty string to disable git.
# ENV DOCKER_MUNKIDO_GIT_PATH = '/usr/bin/git'
# If GIT_BRANCHING is set and the GIT path is specified above, 
# commits are pushed to a new branch.
# ENV DOCKER_MUNKIDO_GIT_BRANCHING = 'yes'
# If DOCKER_MUNKIDO_GIT_IGNORE_PKGS is set and the GIT path is specified above, 
# the 'pkgs' directory is not considered for git commit
# ENV DOCKER_MUNKIDO_GIT_IGNORE_PKGS = 'yes'
# If DOCKER_MUNKIDO_MANIFEST_RESTRICTION_KEY is set, 
# manifests are not restricted by group
# ENV DOCKER_MUNKIDO_MANIFEST_RESTRICTION_KEY = 'restriction'

# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]

# Install python
RUN apt-get update && apt-get install -y \
  openssh-server \
  python-pip \
  python-dev \
  libpq-dev

RUN git clone https://github.com/munki/munki.git /munki-tools
ADD / $APP_DIR
ADD docker/django/requirements.txt $APP_DIR/
RUN pip install -r $APP_DIR/requirements.txt
ADD docker/settings.py $APP_DIR/munkido/
ADD docker/settings_import.py $APP_DIR/munkido/
ADD docker/django/ $APP_DIR/munkido/
RUN mkdir -p /var/log/django
ADD docker/nginx/munkido.conf /etc/nginx/sites-enabled/munkido.conf
ADD docker/run.sh /etc/my_init.d/run.sh
RUN rm -f /etc/service/nginx/down
RUN rm -f /etc/nginx/sites-enabled/default
RUN groupadd munki
RUN usermod -g munki app

VOLUME ["/munki_repo", "/home/docker/munkido" ]
EXPOSE 8000

#     Uncomment the following lines to copy an ssh key to the Docker image 
# in order to allow passwordless `git push`
# This is necessary in Bitbucket, Github, Gitlab etc.
# if you change the ssh-keyscan to the domain you are connecting to, so that you 
# don't have to pass passwords in plain text
#     You will need to add an `id_rsa` file to the same path as the Dockerfile,
# as Docker cannot operate on files outside the current working directory.
#     To generate an SSH key, follow the instructions at:
# https://confluence.atlassian.com/bitbucket/set-up-ssh-for-git-728138079.html
# The id_rsa file will then be found at ~/.ssh

ADD docker/id_rsa /root/.ssh/id_rsa
RUN touch /root/.ssh/known_hosts
RUN chown root: /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa
# This dodgy line necessary for docker-gitlab, since ssh-keyscan doesn't generate the
# correct syntax:
RUN echo "[192.168.168.134]:10022 ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBLz8ILw5mJJZtF7M+HjaGx6jWUDBhKv5sJu0OrS6VBNj598g+iSWzXNZCgS/FtGHcPDnMFIEBDsJgDSLWEbE52Y= " >> /root/.ssh/known_hosts

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*