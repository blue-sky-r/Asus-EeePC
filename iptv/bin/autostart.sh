#!/bin/bash

# ACTIVATE AUTOSTART of APP on Asus Eee PC-701

# cfg file
CFG=~/.config/lxsession/Lubuntu/autostart

#
HEAD="# added by $0 on "$(date "+%F %T")

[ $# -lt 1 ] && cat <<< """
Activate Autostart of app on EEE-PC 701. 

usage: $0 app

The following file will be modified:
$CFG

""" && exit 1

APP=$*

# light dm config
#
echo "$HEAD" >> $CFG
echo $APP >> $CFG

# done
#
echo "Autostart for app $APP activated ..."
ls -l $CFG
cat $CFG
