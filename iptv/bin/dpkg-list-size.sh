#!/bin/bash

# list installed packages size

echo
echo -e "== Package == \t = Size ="

dpkg -l | awk '/^ii/ {print $2}' \
	| xargs -n 1 dpkg-query -s \
	| awk '/^Package:/ {printf "%s\t",$2} /^Installed-Size:/ {print $2}' \
	| sort -nrk 2
	