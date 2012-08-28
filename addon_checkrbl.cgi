#!/usr/bin/perl
#WHMADDON:addonupdates:Nicks <b>RBL Checker</b>
###############################################################################
#   Nick's RBL Checker WHM Plugin
#   Copyright (C) 2008 Nick Pack
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

use Sys::Hostname qw(hostname);
use lib '/usr/local/cpanel';
use Cpanel::cPanelFunctions ();
use Cpanel::Form            ();
use Cpanel::Config          ();
use Whostmgr::HTMLInterface ();
use Whostmgr::ACLS          ();
use Cpanel::SafeFile        ();
use Mail::RBL;
use Regexp::Common qw /URI/;

###############################################################################

my %FORM     = Cpanel::Form::parseform();
my $class1   = "tdshade2";
my $class2   = "tdshade1";
my $count    = 0;
my $re_a_tag = qr/<a\s+.*?>.*<\/a>/si;

print "Content-type: text/html\r\n\r\n";

if ( !$FORM{action} ) {
	Whostmgr::HTMLInterface::defheader( "Nicks RBL Checker",
		'/cgi/checkrbl/chkrbl.gif', '/cgi/addon_checkrbl.cgi' );
}
Whostmgr::ACLS::init_acls();
if ( !Whostmgr::ACLS::hasroot() ) {
	print "You do not have access to view Nicks RBL Checker.\n";
	exit();
}

print
"<style type='text/css'>.Safe { font-weight:bold; text-align:center; padding:5px; display:block; font-size:10px; color:#FFFFFF; background-color: #006633; height: 15px; } .Error { font-weight:bold;  text-align:center; padding:10px; display:block; font-size:14px; color:#FFFFFF; background-color: #FF0000; height: 15px; } #checkrbltbl td { padding:5px; } </style>";

if ( $FORM{action} eq "checkbl" ) {
		
	my $host = $FORM{IPAddr};
	chomp($host);

	my @ip = split /\./, $host;
	if (   4 ne scalar @ip
		|| 4 ne scalar map { $_ =~ /^(0|[1-9]\d*)$/ && $1 < 256 ? 1 : () } @ip )
	{
		print
"<p>Invalid IPv4 Address Specified</p><p>[  <a href='addon_checkrbl.cgi'>Go Back</a> ]</p>";
		exit;
	}
	my $inlock = Cpanel::SafeFile::safeopen(\*BLS,"<","/etc/nrbl/rblists.conf");
	print "<h2>RBL Report for ", $host, "</h2>";
	print "<p>[ <a href='addon_checkrbl.cgi'>Check another IP</a> ]</p>";
	print "<table class=\"sortable\" id=\"checkrbltbl\" width=\"95%\">\n";
	print
"<tr class=\"tblheader\"><th>List</th><th>Status</th><th>List Message/Report URL</th></tr>\n";

	while ( my $line = <BLS> ) {
		chomp($line);
		@curbl = split( /:/, $line );
		my $list = $curbl[1];
		my $rbl  = new Mail::RBL($list);

		if ( $count % 2 == 1 ) {
			$thisclass = $class1;
		}
		else {
			$thisclass = $class2;
		}
		my ($listcheck, $txt) = $rbl->check($host);

		if ( $listcheck) {
			$result = '<span class="Error">LISTED</span>';
		}
		else {
			$result = '<span class="Safe">Not Listed</span>';
		}
		
		my @chunks = split( /($re_a_tag)/si, $txt );

		foreach my $chunks_i (@chunks) {
			next if $chunks_i =~ /$re_a_tag/;
			$chunks_i =~
			  s/($RE{URI}{HTTP})/<a target="_blank" href="$1">$1<\/a>/gsi;
		}

		$txt = join( '', @chunks );
		if ( length($txt) < 1 ) {
			$txt = "<strong>N/A</strong>";
		}
		print "<tr class='", $thisclass, "'><td><strong>", $curbl[0],
		  "</strong><br />", $list, "</td><td>$result</td><td>", $txt,
		  "</td></tr>\n";
		$count++;
	}
	#close(BLS);
	Cpanel::SafeFile::safeclose(\*BLS,$inlock);
	print "</table>";
} else {

print
'<link rel="stylesheet" type="text/css" href="/yui/fonts/fonts-min.css" />
<link rel="stylesheet" type="text/css" href="/yui/container.css" />
<script type="text/javascript" src="/yui/utilities/utilities.js"></script>
<script type="text/javascript" src="/yui/container/container-min.js"></script>
';


	print '<div id="content"><script type="text/javascript">

    YAHOO.namespace("nickrbl.container");

    function init() {

       var content = document.getElementById("content");
       var ipaddr = document.getElementById("IPAddr").value; 
 
        if (!YAHOO.nickrbl.container.wait) {

            // Initialize the temporary Panel to display while waiting for external content to load

            YAHOO.nickrbl.container.wait = 
                    new YAHOO.widget.Panel("wait",  
                                                    { width: "240px", 
                                                      fixedcenter: true, 
                                                      close: false, 
                                                      draggable: false, 
                                                      zindex:4,
                                                      modal: true,
                                                      visible: false
                                                    } 
                                                );
    
            YAHOO.nickrbl.container.wait.setHeader("Checking RBLs, please wait...");
            YAHOO.nickrbl.container.wait.setBody("<img src=\"checkrbl/rel_interstitial_loading.gif\" />");
            YAHOO.nickrbl.container.wait.render(document.body);

        }
	var callback = {
            success : function(o) {
                content.innerHTML = o.responseText;
                content.style.visibility = "visible";
                YAHOO.nickrbl.container.wait.hide();
            },
            failure : function(o) {
                content.innerHTML = o.responseText;
                content.style.visibility = "visible";
                content.innerHTML = "CONNECTION FAILED!";
                YAHOO.nickrbl.container.wait.hide();
            }
        }

        // Show the Panel
        YAHOO.nickrbl.container.wait.show();
	var conn = YAHOO.util.Connect.asyncRequest("GET", "addon_checkrbl.cgi?action=checkbl&IPAddr=" + ipaddr, callback);
        
    }
    
    YAHOO.util.Event.on("Submit", "click", init);
		
</script>';

print ' <label for="IPAddr">Enter an IPv4 Address to Check</label><br />
  <input type="text" name="IPAddr" id="IPAddr" accesskey="1" tabindex="1" />
  <input name="action" type="hidden" value="checkbl" />
  <input type="button" name="Submit" id="Submit" value="Check" />
</div>';

}

if ( !$FORM{action} ) {
	print
"<pre style='font-family: Courier New, Courier; font-size: 12px'>RBL Checker v1b</pre>";
	print
"<p>&copy;2008, <a href='http://www.carbonstudios.co.uk' target='_blank'>Nick Pack</p>\n";
}
1;

