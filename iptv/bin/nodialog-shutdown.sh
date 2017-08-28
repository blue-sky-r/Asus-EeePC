:

# NO DIALOG ON SHUTDOWN

# file to modify
#
FILE=/usr/bin/lxsession-default

# backup and modify
#
cp "$FILE" "$FILE.bak" && awk '	\
	/"quit"\)/ 	{ skip=1 } \
	skip==0 	{ print $0 }  \
	skip==1 && /;;/ { skip=0; \
			print "\"shutdown\"|\"quit\")"; 
			print "\techo \"Request Shutdown\"";
			print "\tdbus-send --session --print-reply --dest=\"org.lxde.SessionManager\" /org/lxde/SessionManager org.lxde.SessionManager.RequestShutdown";
			print "\t;;" }' \
	"$FILE.bak" > "$FILE"
	
echo "$FILE modified ..."
