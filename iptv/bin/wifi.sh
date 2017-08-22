#!/bin/bash

# ACTIVATE WiFi and Ethernet on Asus Eee PC-701

# dst files will be recreated/owerwritten
IDST=/etc/network/interfaces
WDST=/etc/wpa_supplicant.conf
#
HEAD="# created by $0 on "$(date "+%F %T")

[ $# -lt 2 ] && cat <<< """
Activate WiFi on Ausu EEE-PC 701. 

usage: $0 'ssid' 'passphrase'

The following files will be overwritten:
$IDST
$WDST

Must be executed as root (use sudo $0) !
""" && exit 1

# interfaces
#
echo "$HEAD" > $IDST
echo >> $IDST
echo "auto lo" >> $IDST
echo >> $IDST
echo "iface lo inet loopback" >> $IDST
echo >> $IDST
echo "auto eth0" >> $IDST
echo >> $IDST
echo "iface eth0 inet dhcp" >> $IDST
echo >> $IDST
echo "auto wlan0" >> $IDST
echo >> $IDST
echo "iface wlan0 inet dhcp" >> $IDST
echo -e "\t pre-up wpa_supplicant -Dwext -B  -i wlan0 -c /etc/wpa_supplicant.conf" >> $IDST
echo -e "\t post-down killall -q wpa_supplicant" >> $IDST
echo >> $IDST

# wpa_supplicant
#
ssid=$1
pass=$2

echo "$HEAD" > $WDST
echo >> $WDST
echo "ctrl_interface=/var/run/wpa_supplicant" >> $WDST
echo >> $WDST
wpa_passphrase "$ssid" "$pass" >> $WDST
echo >> $WDST

# done
#
echo "WiFi configured ..."
ls -l $IDST
cat $IDST
ls -l $WDST
cat $WDST
