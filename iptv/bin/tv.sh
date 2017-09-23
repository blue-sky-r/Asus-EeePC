#!/usr/bin/env bash

# HLS bitrate
#
RATE=auto

# iptv channel list
#
PLAYLIST="tv.m3u8"

# log to syslog (empty for no logging)
#
LOGT="UPDATE $PLAYLIST"

# backup
#
BAK="${PLAYLIST}.bak"

# update url
#
URL="http://url-to-update/iptv"

# backup current
#
cp "$PLAYLIST" "$BAK"

# try to update, return the last by one line
#
msg=$( wget -N "$URL/$PLAYLIST" 2>&1 | tail -2 | head -1 )

# optional log
#
[ ! -z "$LOGT" ] && logger -t "$LOGT" "$msg"

# use backup if downloaded playlist is empty
#
[ ! -s "$PLAYLIST" ] && cp "$BAK" "$PLAYLIST"

# start iptv player
#
mpv --hls-bitrate=$RATE "$PLAYLIST"

