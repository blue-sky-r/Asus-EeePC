#!/bin/bash

# INSTALL

# system packages
#
PKG="software-properties-common python3-software-properties lirc joe mc dropbear mini-httpd socat"

# additional repositories
#
#PPA="ppa:rvm/smplayer"
PPA="ppa:mc3man/trusty-media ppa:mc3man/mpv-tests"

# multimedia packages
#
MM="ffmpeg mpv"

# do not ask confirmation
#
YES="--yes"

# system packages
#
for name in $PKG
{
	sudo apt-get $YES install "$name"
}

# ppa repositories
#
for name in $PPA
{
	sudo add-apt-repository $YES "$name"
}

sudo apt-get update
sudo apt-get upgrade

# multimedia packages
#
for name in $MM
{
	sudo apt-get $YES install "$name"
}
