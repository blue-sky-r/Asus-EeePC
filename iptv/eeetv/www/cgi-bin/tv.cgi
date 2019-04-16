#!/bin/bash

# version tag
#
VER="2019.04.15"

# debug output to the caller (will show as pop-up alert)
#
DBG=

echo "Content-Type: text/plain"; echo

[ $DBG ] && (echo "DBG: QUERY_STRING:${QUERY_STRING}"; echo)

# json
#
function json
{
    local key=$1
    python -c "import sys, json; print json.load(sys.stdin).get($key)"
}

# split by &
#
for keyval in ${QUERY_STRING//&/ }
{
	# split key=val
	#
	key=${keyval%=*}
	val=${keyval#*=}
	
	# + -> space
	val=${val//+/ }
	# %xy -> char
	val=$( printf '%b' "${val//%/\\x}" )

	[ $DBG ] && echo "keyval($keyval) => key($key) val($val)"

    # use the first key as command CMD
    #
	[ -z "$CMD" ] && CMD=$key

    # define parametric variable assignment
    #
    [ -n "$val" ] && declare -r ${key//-/_}="$val" && [ $DBG ] && echo "declared variable ${key//-/_} = $val"
}

# execute command CMD
#
case $CMD in

    # channel=cnn
    channel)	r=$( echo "script-message-to channel_by_name channel \"$channel\"" | socat - /tmp/mpvsocket )
                ;;

    # survey-range-playlist=playlist & start=name & end=name [& osd=message]
    survey-range-playlist)
                # survey_range_playlist "chan 1" "chan 10" ["playlist.m3u8" ["OSD message"]]
                r=$( echo "script-message-to channel_survey survey_range_playlist \
                    \"${start}\" \"${end}\" \"${survey_range_playlist}\" \"${osd}\" " \
                    | socat - /tmp/mpvsocket )
                ;;

    # survey-list-playlist=playlist & list=list [ & osd=message]
    survey-list-playlist)
                # survey_list_playlist "chan 1,chan 10" ["playlist.m3u8" ["OSD message"]]
                r=$( echo "script-message-to channel_survey survey_list_playlist \
                    \"${list}\" \"${survey_list_playlist}\" \"${osd}\" " \
                    | socat - /tmp/mpvsocket )
                ;;

    # show-text=test msg
    show-text)	r=$( echo "show-text \"${show_text}\"" | socat - /tmp/mpvsocket )
                ;;

    # show-text=test msg with ass control codes
    show-text-ass-cc)
                # get control code for disabling escaping ass sequences
    	        #escdis=$( echo '{ "command": ["get_property", "osd-ass-cc/0"] }' | socat - /tmp/mpvsocket | awk -F'"' '/data/ {print $4}' )
    	        #
    	        #escdis='\xfd{\\fs10}'
                #r=$( echo "show-text \"Norm:${escdis}${show_text_ass_cc}\"" | socat - /tmp/mpvsocket )
    	        esc0='\xfd'
                r=$( echo "show-text \"${esc0}${show_text_ass_cc}\" 20000"| socat - /tmp/mpvsocket )
                #r=$( echo "show-text \"${escdis}${show_text_ass_cc//\\/\\\\}\"" | socat - /tmp/mpvsocket )
                #r=$( echo "{\"command\": [\"show_text\", \"${esc0}${show_text_ass_cc}\"] }" | socat - /tmp/mpvsocket )
                ;;

    # clock
    clock)		r=$( echo "keypress h" | socat - /tmp/mpvsocket )
                ;;

    # email
    email)		r=$( echo "keypress e" | socat - /tmp/mpvsocket )
                ;;

    # weather
    weather)	r=$( echo "keypress w" | socat - /tmp/mpvsocket )
                ;;

    # info
    info)		r=$( echo "keypress i" | socat - /tmp/mpvsocket )
                ;;

    # get active channel title/name (json)
    get-title)	json=$( echo '{ "command": ["get_property", "media-title"] }' | socat - /tmp/mpvsocket )
                # output json: {"data":"Wau,,0","error":"success"}
                echo "$json"
                ;;

    # get program
    get-epg)    json=$( ./epg.py -title "${channel}" -offset "${offset}" -bar "${barsize}" -epg )
                # output
                echo "$json"
                ;;

    # mpv --list-properties
    # echo '{ "command": ["get_property", "video-out-params"] }'  | socat - /tmp/mpvsocket
    # {"data":{"pixelformat":"yuv420p","average-bpp":12,"plane-depth":8,"w":640,"h":360,"dw":640,"dh":360,"aspect":1.777778,
    # "par":1.000000,"colormatrix":"bt.601","colorlevels":"limited","primaries":"bt.709","gamma":"bt.1886","sig-peak":1.000000,
    # "light":"display","chroma-location":"mpeg2/4/h264","stereo-in":"mono","rotate":0},"error":"success"}
    # get active channel title/name (json)
    get-property)
                json=$( echo '{ "command": ["get_property", "'${get_property}'"] }' | socat - /tmp/mpvsocket )
                # output json
                echo "$json"
                ;;

    *)		    echo "unrecognized command:$CMD - query:$QUERY_STRING"
                ;;
esac

# result output from mpv socket
#
[ $DBG ] && echo $r

