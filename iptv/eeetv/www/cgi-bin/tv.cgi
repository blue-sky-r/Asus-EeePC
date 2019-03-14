#!/bin/bash

# debug output to the caller (will show as pop-up alert)
#
DBG=

echo "Content-Type: text/plain"; echo

[ $DBG ] && echo "QUERY_STRING:${QUERY_STRING}"

for keyval in ${QUERY_STRING//&/ }
{
	[ $DBG ] && (echo; echo "keyval($keyval)")
	
	cmd=${keyval%=*}
	par=${keyval#*=}
	
	# + -> space
	par=${par//+/ }
	# %xy -> char
	par=$( printf '%b' "${par//%/\\x}" )

	[ $DBG ] && echo "cmd($cmd) par($par)"

	case $cmd in

		channel)	r=$( echo "script-message-to channel_by_name channel \"$par\"" | socat - /tmp/mpvsocket )
				;;
				
		show-text)	r=$( echo "show-text \"$par\"" | socat - /tmp/mpvsocket )
				;;

		clock)		r=$( echo "keypress h" | socat - /tmp/mpvsocket )
				;;
								
		email)		r=$( echo "keypress e" | socat - /tmp/mpvsocket )
				;;
								
		weather)	r=$( echo "keypress w" | socat - /tmp/mpvsocket )
				;;

		info)		r=$( echo "keypress i" | socat - /tmp/mpvsocket )
				;;
												
		*)		echo "unrecognized parameter: $keyval"
				;;
	esac	
}

[ $DBG ] && echo $r

