# This is a standalone Dockerfile for Docker Hub. The Munki-Do git repository
# has a Dockerfile in the root directory which does away with the need to clone the
# docker-munki-do repository. So you normally won't need this one.

# Use phusion/passenger-full as base image. To make your builds reproducible, make
# sure you lock down to a specific version, not to `latest`!
# See https://github.com/phusion/passenger-docker/blob/master/Changelog.md for
# a list of version numbers.
FROM phusion/passenger-full:0.9.17
MAINTAINER Graham Pugh <g.r.pugh@gmail.com>

# Set correct environment variables.
ENV HOME /root
ENV DEBIAN_FRONTEND noninteractive
ENV APP_DIR /home/app/munkido
ENV TIME_ZONE America/New_York
ENV APPNAME Munki-Do

# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]

# Install python
RUN apt-get update && apt-get install -y \
  openssh-server \
  python-pip \
  python-dev \
  libpq-dev

RUN git clone https://github.com/munki/munki.git /munki-tools
RUN git clone https://github.com/grahampugh/munki-do.git $APP_DIR
ADD django/requirements.txt $APP_DIR/
RUN pip install -r $APP_DIR/requirements.txt
RUN touch /root/tmp.txt
ADD django/ $APP_DIR/munkido/
RUN mkdir -p /var/log/django
ADD nginx/munkido.conf /etc/nginx/sites-enabled/munkido.conf
ADD run.sh /etc/my_init.d/run.sh
RUN rm -f /etc/service/nginx/down
RUN rm -f /etc/nginx/sites-enabled/default
RUN groupadd munki
RUN usermod -g munki app

VOLUME ["/munki_repo", "/home/app/munkido" ]
EXPOSE 8000

#     Uncomment the following lines to copy an ssh key to the Docker image 
# in order to allow passwordless `git push`
# This is necessary in Bitbucket and should also work in Github
# if you change the ssh-keyscan to `github.com`, so that you 
# don't have to pass passwords in plain text
#     You will need to add an `id_rsa` file to the same path as the Dockerfile,
# as Docker cannot operate on files outside the current working directory.
#     To generate an SSH key, follow the instructions at:
# https://confluence.atlassian.com/bitbucket/set-up-ssh-for-git-728138079.html
# The id_rsa file will then be found at ~/.ssh

ADD id_rsa /root/.ssh/id_rsa
RUN touch /root/.ssh/known_hosts
RUN chown root: /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa
RUN ssh-keyscan bitbucket.org >> /root/.ssh/known_hosts

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
