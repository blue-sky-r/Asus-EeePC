#!/usr/bin/env bash

# evaluate environment variables in playlist
#
VERSION="2019.05.01"

SRC_M3U8=$1
DST_M3U8=$2

# optional tag for logger
#
LOGT="envsubst-playlist"

# only update if older than (empty = akways update)
#
OLDER='now - 2 hours'

# debug
#
DBG=

[ $# -lt 1 ] && cat <<< """
usage: $0 source.m3u8 [result.m3u8]

source.m3u8 ... m3u8 playlist with variables
result.m3u8 ... m3u8 playlist with expanded variables

""" && exit 1

# do not update if result playlist is newer then limit $OLDER
#
if [ -n "$OLDER" ]
then
        playlist_time=$(date -r "$DST_M3U8" +%s)
        limit=$(date -d "$OLDER" +%s)
        # is playlist newer than limit ?
        if [ $playlist_time -gt $limit ]
        then
            [ -n "$LOGT" ] && logger -t "$LOGT" "Playlist($DST_M3U8) not older than $OLDER, skipping update"
            exit 1
        fi
fi

# include tokens
#
DIR=${0%/*}
source "$DIR/get_auth_tokens.sh" "USTVGO TA3 STVx DOMA DAJTO HRONKA INFOVOJNA"
#source "$DIR/get_auth_tokens.sh" "USTVGO TA3 STVx HRONKA INFOVOJNA"

[ $DBG ] && echo -e " AUTH_USTVGO: $AUTH_USTVGO \n AUTH_TA3: $AUTH_TA3 \n STV1: $HTTP_STV1 \n" \
         && echo -e " DAJTO: $HTTP_DAJTO \n DOMA: $HTTP_DOMA \n MARKIZA: $HTTP_MARKIZA \n" \
         && echo -e " HRONKA: $HTTP_HRONKA \n INFOVOJNA: $HTTP_INFOVOJNA \n"

# log
#
if [ -n "$LOGT" ]
then
    logger -t "$LOGT" "UPDATE playlist($DST_M3U8) envsubst-playlist version $VERSION"
    logger -t "$LOGT" "AUTH_USTVGO: $AUTH_USTVGO"
    logger -t "$LOGT" "AUTH_TA3: $AUTH_TA3"
    logger -t "$LOGT" "HTTP_STV1: $HTTP_STV1"
    logger -t "$LOGT" "HTTP_DAJTO: $HTTP_DAJTO"
    logger -t "$LOGT" "HTTP_DOMA: $HTTP_DOMA"
    logger -t "$LOGT" "HTTP_MARKIZA: $HTTP_MARKIZA"
    logger -t "$LOGT" "HTTP_HRONKA: $HTTP_HRONKA"
    logger -t "$LOGT" "HTTP_INFOVOJNA: $HTTP_INFOVOJNA"
fi

if [ $DST_M3U8 ]
then
    envsubst < "$SRC_M3U8" > "$DST_M3U8"
else
    envsubst < "$SRC_M3U8"
fi
