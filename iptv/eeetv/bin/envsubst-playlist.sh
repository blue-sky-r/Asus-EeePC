#!/usr/bin/env bash

# evaluate environment variables in playlist
#
VERSION="2019.05.09"

SRC_M3U8=$1
DST_M3U8=$2
FORCE_EVAL=$3

# optional tag for logger (epmty = no logging)
#
LOGT="envsubst-playlist"

# only update if older than (empty = always update)
#
OLDER='now - 1 hour - 35 mins'

# debug (print log messages to stdout)
#
DBG=

[ $# -lt 1 ] && cat <<< """
usage: $0 source.m3u8 [result.m3u8 [force]]

source.m3u8 ... m3u8 playlist with variables
result.m3u8 ... m3u8 playlist with expanded variables
force       ... any string will force env.subst (default no, only if older than '$OLDER')

""" && exit 1

# debug or logger output
#
function msg()
{
    [   $DBG ] && echo -e "$LOGT $1"
    [ ! $DBG ] && [ -n "$LOGT" ] && logger -t "$LOGT" "$1"
}

# startup msg - show parameters
#
msg "ver. $VERSION - src($SRC_M3U8) dst($DST_M3U8) force($FORCE_EVAL)"

# $OLDER condition provided and dst playlist exists and has size>0
#
if [ -n "$OLDER" -a -n "$DST_M3U8" -a -s "$DST_M3U8" ]
then
        playlist_time=$(date -r "$DST_M3U8" +%s)
        limit=$(date -d "$OLDER" +%s)
        # exit if result playlist is newer then limit $OLDER and force_eval not requested
        if [ $playlist_time -gt $limit -a -z "$FORCE_EVAL" ]
        then
            msg "playlist [ $(ls -l $DST_M3U8) ] not older than [ $OLDER ], skipping update"
            exit 1
        fi
fi

# include tokens
#
DIR=${0%/*}
source "$DIR/get_auth_tokens.sh" "USTVGO TA3 STVx DOMA DAJTO HRONKA INFOVOJNA"
#source "$DIR/get_auth_tokens.sh" "USTVGO TA3 STVx HRONKA INFOVOJNA"

# dbg or log
#
msg "AUTH_USTVGO: $AUTH_USTVGO"
msg "HTTP_TA3: $HTTP_TA3"
msg "HTTP_STV1: $HTTP_STV1"
msg "HTTP_DAJTO: $HTTP_DAJTO"
msg "HTTP_DOMA: $HTTP_DOMA"
msg "HTTP_MARKIZA: $HTTP_MARKIZA"
msg "HTTP_HRONKA: $HTTP_HRONKA"
msg "HTTP_INFOVOJNA: $HTTP_INFOVOJNA"

# if destinaton requested create dst file, otherwise output to stdout
#
if [ -n "$DST_M3U8" ]
then
    envsubst < "$SRC_M3U8" > "$DST_M3U8"
    msg "updated [ $(ls -l $DST_M3U8) ]"
else
    envsubst < "$SRC_M3U8"
fi

