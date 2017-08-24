#!/bin/bash

# ACTIVATE AUTOSTART of TV on Asus Eee PC-701

APP=mpv
CFG=~/.config/mpv/tv.m3u8
CFG=tv.m3u8

bin/autostart.sh $APP $CFG
