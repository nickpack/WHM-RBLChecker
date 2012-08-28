#!/bin/bash
ROOT_UID=0

if [ "$UID" -eq "$ROOT_UID" ]  # Will the real "root" please stand up?
then
	echo "Nick's RBL Checker Installation"
	echo "Installing Required Perl Modules..."
		/scripts/realperlinstaller Mail::RBL
		/scripts/realperlinstaller Regexp::Common
	echo "Adding Default Configuration..."
		mkdir /etc/nrbl
		cp -v rblists.conf /etc/nrbl
	echo "Installing WHM Plugin Resources..."
		mkdir /usr/local/cpanel/whostmgr/docroot/cgi/checkrbl
		cp -v *.gif /usr/local/cpanel/whostmgr/docroot/cgi/checkrbl
		echo "Installing WHM Plugin..."
		cp -v addon_checkrbl.cgi /usr/local/cpanel/whostmgr/docroot/cgi
	echo "Done."
else
  echo "You need to run this script as root, cannot continue"
fi
exit
