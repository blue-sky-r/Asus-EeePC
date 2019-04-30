#!/usr/bin/env bash

# evaluate environment variables in playlist
#

SRC_M3U8=$1
DST_M3U8=$2

# debug
#
DBG=

[ $# -lt 1 ] && cat <<< """
usage: $0 source.m3u8 [result.m3u8]

source.m3u8 ... m3u8 playlist with variables
result.m3u8 ... m3u8 playlist with expanded variables

""" && exit 1

# include tokens
#
DIR=${0%/*}
source "$DIR/get_auth_tokens.sh" "USTVGO TA3 STVx DOMA DAJTO"

[ $DBG ] && echo -e " AUTH_USTVGO: $AUTH_USTVGO \n AUTH_TA3: $AUTH_TA3 \n STV1: $HTTP_STV1 \n DAJTO: $HTTP_DAJTO \n DOMA: $HTTP_DOMA \n MARKIZA: $HTTP_MARKIZA"

if [ $DST_M3U8 ]
then
    envsubst < "$SRC_M3U8" > "$DST_M3U8"
else
    envsubst < "$SRC_M3U8"
fi
