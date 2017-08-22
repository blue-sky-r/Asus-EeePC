#!/bin/bash

# ACTIVATE AUTOLOGIN on Asus Eee PC-701

# dst files will be recreated/owerwritten
DST=/etc/lightdm/lightdm.conf
#
HEAD="# created by $0 on "$(date "+%F %T")

[ $# -lt 1 ] && cat <<< """
Activate AutologinEEE-PC 701. 

usage: $0 user

The following file will be overwritten:
$DST

Must be executed as root (use sudo $0) !
""" && exit 1

USR=$1

# light dm config
#
echo "$HEAD" > $DST
echo >> $DST
echo "[SeatDefaults]" >> $DST
echo "autologin-user=$USR" >> $DST
echo "autologin-user-timeout=0" >> $DST
echo "user-session=Lubuntu" >> $DST
echo "greeter-session=lightdm-gtk-greeter" >> $DST
echo >> $DST

# done
#
echo "Autologin for user $USR activated ..."
ls -l $DST
cat $DST
