:

# result config
#
conf=lircd-${1:irrecord}.conf

# ignore namespace
#
#ns="-n"

echo
echo "$0 - recording lirc config: $conf"
echo

irrecord -d hw:0@44100,l -H audio_alsa $ns $conf

echo
echo "$0 - done, copy lirc config: $conf to /etc/lirc/lircd.conf"
echo

