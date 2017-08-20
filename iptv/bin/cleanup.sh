#!/bin/bash

# POST-INSTALL CLEANUP

# NOTE; removing cups breaks system
#
PKGS="bluez hplip printer-driver ppp "

# fonts
#
FONTS="tlwg kacst khmeros lao lklug sil takao tibetan"

# ttf fonts
#
TTFS="indic- kochi- punjabi-"

# xorg video drivers
#
XVIDS="ati cirrus mach64 mga neomagic noveau openchrome qxl r128 radeon s3 savage siliconmotion sis sisusb tdfx trident vmware"

# do not ask confirmation
#
YES="--yes"

# 
function remove_pkgs
{
	local filter=$1
	
	echo
	echo "= finding pkgs for filter: $filter ="

	for pkg in $( dpkg -l | awk '{print $2}' | grep "$filter" | grep -v libcups2 )
	{
		echo
		echo "- removing pkg: $pkg ..."
		sudo apt-get $YES purge "$pkg"
	}

}

# packages
#
for name in $PKGS
{	
	remove_pkgs "$name"
}

# fonts
#
for name in $FONTS
{	
	remove_pkgs "fonts-$name"
}

# ttf
#
for name in $TTFS
{	
	remove_pkgs "ttf-$name"
}

# Xorg video drivers
#
for pkg in $XVIDS
{
	remove_pkgs "xserver-xorg-video-$pkg"
}

sudo apt-get clean
sudo apt-get autoremove
