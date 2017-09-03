:

#arecord -V stereo -c 2 -D hw:0 -r 8000 -f S16_LE /dev/null
#arecord -V stereo -c 2 -D plughw:0 -r 8000 -f S16_LE /dev/null
arecord -V stereo -c 2 -D hw:0 -r 44100 -f S16_LE /dev/null
 