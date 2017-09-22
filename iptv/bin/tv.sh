#!/usr/bin/env bash

# HLS bitrate
#
RATE=auto

# iptv channel list
#
PLAYLIST="tv.m3u8"

# backup
#
BAK="${PLAYLIST}.bak"

# update url
#
URL="http://url-to-update/iptv"

# backup current
#
cp "$PLAYLIST" "$BAK"

# try to update
#
wget -q -N "$URL/$PLAYLIST"

# use backup if empty
#
[ ! -s "$PLAYLIST" ] && cp "$BAK" "$PLAYLIST"

# iptv
#
mpv --hls-bitrate=$RATE "$PLAYLIST"

#
#clear
