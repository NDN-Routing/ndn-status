#!/usr/bin/python
#coding=utf-8

############
# Imports. #
############
import socket
import time
from collections import defaultdict

start = time.time()

################################################
# Delcaring and initializing needed variables. #
################################################
localdir = '/ndn/python_script'
links_list	 = []

prefix_timestamp = {}
link_timestamp	 = {}
host_name	 = {}
topology 	 = {}

set_topology	 = defaultdict(set)
router_links 	 = defaultdict(set)
router_prefixes	 = defaultdict(set)

##############################
# Functions to process data. #
##############################
def process_topo():
	links = set
        
	for router, links in router_links.items():
		for link in links:
			if not topology.has_key((router, link)):
				topology[router, link] = 'SkyBlue'
			else:
				topology[router, link] = 'Lime'

def prefix_table():
	print '\t<table id="box-table-a" class="one">'
	print '\t\t<thead>'
	print '\t\t\t<tr>'
	print '\t\t\t\t<th class="border_left" scope="col">Router</th>'
	print '\t\t\t\t<th scope="col">Timestamp</th>'
	print '\t\t\t\t<th scope="col">Prefix</th>'
	print '\t\t\t\t<th class="border_right" scope="col">Status</th>'
	print '\t\t\t</tr>'
	print '\t\t</thead>'
	print '\t\t<tbody>'

	status = 'Online'
	prefixes = set
	switch = True

	for router in sorted(set_topology.keys()):
		prefixes = router_prefixes[router]

		if not prefixes:
			router_prefixes[router].add('-')
			status = 'Offline'
		else:
			status = 'Online'

		if switch:
			print '\t\t<tr class="odd">'
			switch = False
		else:
			print '\t\t<tr>'
			switch = True

		size = str(len(prefixes))
		print '\t\t\t<td rowspan="' + size + '">' + router + '</td>'

		for prefix in prefixes:
			if prefix_timestamp.has_key(prefix):
				timestamp = time.asctime(time.localtime(float(prefix_timestamp[prefix]))) + ' ' + timezone

				if (float(time.time()) - float(prefix_timestamp[prefix])) > 2400 and status == 'Online':
                                	status = 'Out-of-date'
			else:
				timestamp = '-'
			
			if not switch:
				print '\t\t\t<td class="odd">' + timestamp + '</td>'
				print '\t\t\t<td class="odd">' + prefix + '</td>'
				print '\t\t\t<td id="' + status + '">' + status + '</td>'
			else:
				print '\t\t\t<td>' + timestamp + '</td>'
                                print '\t\t\t<td>' + prefix + '</td>'
				print '\t\t\t<td id="' + status + '">' + status + '</td>'
			print '\t\t</tr>'		
	
	print '\t</tbody>'
	print '\t<tfoot><tr><td colspan="4"></td></td></tfoot>'
	print '\t</table>'

def links_table():
	print '\t<table id="box-table-a">'
        print '\t\t<thead>'
        print '\t\t\t<tr>'
        print '\t\t\t\t<th class="border_left" scope="col">Router</th>'
        print '\t\t\t\t<th scope="col">LSA Timestamp</th>'
        print '\t\t\t\t<th class="border_right" scope="col">Links</th>'
        print '\t\t\t</tr>'
        print '\t\t</thead>'
        print '\t\t<tbody>'

	links = set
	switch = True

	for router, links in sorted(router_links.items()):
		size = str(len(links))

		if switch:
			print '\t\t<tr class="odd">'
			switch = False
		else:
			print '\t\t<tr>'
			switch = True

		print '\t\t\t<td rowspan="' + size + '">' + router + '</td>'
	
		if link_timestamp.has_key(router):
			timestamp = time.asctime(time.localtime(float(link_timestamp[router]))) + ' ' + timezone
		else:
			timestamp = '-'

		print '\t\t\t<td rowspan="' + size + '">' + timestamp + '</td>'
		
		for link in links:
			if float(time.time() - (float(link_timestamp[link]))) > 2400 and topology[router, link] == 'Lime':
				status = 'Out-of-date'
			else:
				status = topology[router, link]

			print '\t\t\t<td id="' + status + '">' + link + '</td></tr>'
		
		print '\t\t</tr>'

	print '\t<tfoot><tr><td colspan="3"></td></td></tfoot>'
	print '\t</tbody>'
	print '\t</table>'
			

#############################################################################################
# Read the configuration file to find the last file timestamp, last timestamp and timezone. #
#############################################################################################
with open (localdir + '/parse.conf') as f:
        for line in f:
                line = line.rstrip()

                if 'lastfile' in line:
                        keyword, value = line.split('=', 1)
                        lastfile = value
                        lastfilestamp = value.rstrip('.log')
                        continue

                if 'lasttimestamp' in line:
                        keyword, value = line.split('=', 1)
                        lasttimestamp = value
                        continue

                if 'timezone' in line:
                        keyword, value = line.split('=', 1)
                        timezone = value
                        continue

		if 'timetaken' in line:
			keyword, value = line.split('=', 1)
			timetaken = value
			continue

######################################################
# Read in prefixes, links, timestamps, and topology. #
######################################################
with open (localdir + '/topology') as f:
	while 1:
		line = (f.readline()).rstrip()
		if not line: break

		if 'Router' in line:
			extra, router = line.split(':', 1)

			if router == '64.57.23.210':
                                router_name = 'sppsalt1.arl.wustl.edu'
                        elif router == '64.57.23.178':
                                router_name = 'sppkans.arl.wustl.edu'
                        elif router == '64.57.23.194':
                                router_name = 'sppwash1.arl.wustl.edu'
                        elif router == '64.57.19.226':
                                router_name = 'sppatla1.arl.wustl.edu'
                        elif router == '64.57.19.194':
                                router_name = 'spphous1.arl.wustl.edu'
                        elif router == '162.105.146.26':
                                router_name = '162.105.146.26'
                        else:
                                router_name, extra1, extra2 = socket.gethostbyaddr(router)

                        host_name[router] = router_name

	f.seek(0)

        while 1:
                line = (f.readline()).rstrip()
                if not line: break

                if 'Router' in line:
                        extra, router = line.split(':', 1)
			router_name = host_name[router]

                        while not 'END' in line:
                                line = (f.readline()).rstrip()
                                if not line: break
                                if 'END' in line: break

                                linkID, status = line.split(':', 1)
				link_name = host_name[linkID]
				set_topology[router_name].add(link_name)
                                topology[router_name, link_name] = status

with open (localdir + '/prefix') as f:
        for line in f:
                line = line.rstrip()
                if not line: break

                prefix, router, timestamp = line.split(':', 2)
		router_name = host_name[router]
                router_prefixes[router_name].add(prefix)
                prefix_timestamp[prefix] = timestamp

with open (localdir + '/links1') as f:
        while 1:
                line = (f.readline()).rstrip()
                if not line: break

                if 'Router' in line:
                        extra, router = line.split(':', 1)
			router_name = host_name[router]

                        while not 'END' in line:
                                line = (f.readline()).rstrip()
                                if not line: break
                                if 'END' in line: break

                                linkID, extra = line.split(':', 1)
				link_name = host_name[linkID]
                                router_links[router_name].add(link_name)

with open (localdir + '/link_timestamp') as f:
	for line in f:
		line = line.rstrip()
		if not line: break

		link, timestamp = line.split(':', 1)
		link_name = host_name[link]
		link_timestamp[link_name] = timestamp

process_topo()


################
# Output HTML. #
################
print '<html>'
print '<head>'
print '<meta charset="utf-8">'
print '<title>NDN · Routing Status</title>'
print '\t<link href="http://fonts.googleapis.com/css?family=Rambla:400,700|Istok+Web:400,700" rel="stylesheet" type="text/css">'
print '\t<link rel="stylesheet" type="text/css" href="style.css" />'
print '</head>'
print '<body>'

print '<div id="contentwrapper">'
print '\t<div id="header">'
print '\t\t<div id="title">'
print '\t\t\t<h1>NDN ·</span> <span id="grey">routing</span> <span id="green">status</span></h1>'
print '\t\t</div>'

end = time.time() - start
totaltime = float(end) + float(timetaken)
print '<div id="speed">'
print '<h5>Dynamically produced in ' + "{0:.4f}".format(totaltime) + ' seconds.</h5>'
print '</div>'


print '\t\t<div id="navbar">'
print '\t\t\t<ul>'
print '\t\t\t\t<li><a href="#">home</a></li>'
print '\t\t\t\t<li><a href="#" class="active">status</a></li>'
print '\t\t\t\t<li><a href="#">archive</a></li>'
print '\t\t\t\t<li><a href="#">operators</a></li>'
print '\t\t\t\t<li><a href="#">topology</a></li>'
print '\t\t\t</ul>'
print '\t\t</div>'
print '\t</div>'

print '\t<div id="infodiv">'
print '\t\t<div class="titles"><p>Status information:</p></div>'
print '\t\t<table id="information">'
curtime = time.asctime(time.localtime(time.time())) + ' ' + timezone
timestamp = time.asctime(time.localtime(float(lasttimestamp))) + ' ' + timezone
print '\t\t\t<tr><td><p>Page last updated:</p></td><td>&nbsp;&nbsp;&nbsp;</td><td><p id="green">' + curtime + '</p></td></tr>'
print '\t\t\t<tr><td><p>Last logfile processed:</p></td><td>&nbsp;&nbsp;&nbsp;</td><td><p id="green">' + lastfile + '</p></td></tr>'
print '\t\t\t<tr><td><p>Last timestamp in logfile:</p></td><td>&nbsp;&nbsp;&nbsp;</td><td><p id="green">' + timestamp + '</p></td></tr>'
print '\t\t</table>'
print '\t\t<table id="legend">'
print '\t\t\t<tr><td bgcolor="#4AA02C" width="50"></td><td>&nbsp;&nbsp;&nbsp;</td><td><p id="green">Online</p></td></tr>'
print '\t\t\t<tr><td bgcolor="#E41B17" width="50"><td>&nbsp;&nbsp;&nbsp;</td><td><p id="green">Offline</p></td></tr>'
print '\t\t\t<tr><td bgcolor="#BDEDFF" width="50"><td>&nbsp;&nbsp;&nbsp;</td><td><p id="green">Online, not part of topology</p></td></tr>'
print '\t\t\t<tr><td bgcolor="#FBB917" width="50"><td>&nbsp;&nbsp;&nbsp;</td><td><p id="green">Out-of-date timestamp (no update for 40 minutes)</p></td></tr>'
print '\t\t</table>'
print '\t</div>'

print '\t<div id="wrap">'
print '\t\t<a name="advertised_prefix">'
print '\t\t<div class="titles2"><p>Advertised Prefixes:</p></div>'
prefix_table()

print '<a name="link_status">'
print '<div class="titles2"><p>Links Status:</p></div>'
links_table()
print '\t</div>'

print '</div>'
print '<div id="leftcolumn"></div>'
print '<div id="rightcolumn"></div>'
print '</body>'
print '</html>'

end = time.time() - start
print str(end)

