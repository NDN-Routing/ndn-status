#!/usr/bin/python

############
# Imports. #
############
import os
import time
from collections import defaultdict

start = time.time()

################################################
# Delcaring and initializing needed variables. #
################################################
localdir = '/ndn/python_script'

router_prefixes	 = {}
prefix_timestamp = {}
link_timestamp 	 = {}

router_links	 = defaultdict(set)

#############################################################################################
# Read the configuration file to find the log directory, last log file, and last line read. #
#############################################################################################
with open (localdir + '/parse.conf') as f:
	for line in f:
		line = line.rstrip()
		
		if 'logdir' in line:
			keyword, value = line.split('=', 1)
			logdir = value
			continue

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

		if 'lastbyte' in line:
			keyword, value = line.split('=', 1)
                        lastbyte = float(value)
                        continue

###################################
# Read in prefix and links files. #
###################################
with open (localdir + '/prefix') as f:
	for line in f:
		line = line.rstrip()
		if not line: break
		
		prefix, router, timestamp = line.split(':', 2)
		router_prefixes[prefix] = router
		prefix_timestamp[prefix] = timestamp
		
with open (localdir + '/links') as f:
        while 1:
                line = (f.readline()).rstrip()
		if not line: break

                if 'Router' in line:
                        extra, router = line.split(':', 1)

                        while not 'END' in line:
                                line = (f.readline()).rstrip()
                                if not line: break
                                if 'END' in line: break

                                linkID, linkdata = line.split(':', 1)
                                router_links[router].add((linkID, linkdata))

with open (localdir + '/link_timestamp') as f:
	for line in f:
		line = line.rstrip()
		if not line: break
		
		router, timestamp = line.split(':', 1)
		link_timestamp[router] = timestamp

# Read in names of all files in the log directory and add them to the file array.
directory = os.listdir(logdir)
directory.sort();

######################################################################################
# Starting with the last file read, jump to the last read byte and continue parsing. #
######################################################################################
for cur in directory:
	if lastfilestamp > cur.rstrip('.log'):
		continue
	
	with open (logdir + '/' + cur) as f:
		if lastfilestamp == cur.rstrip('.log'):
                	f.seek(lastbyte)

		while 1:
			line = (f.readline()).rstrip()
			if not line: break

			left, right = line.split(':', 1)
			timestamp, extra = left.split('-', 1)
			line = right

			# Warning: there is a double space!
			if 'Opaque Type  236' in line:
				while (not 'lsa_read called' in line) and (not 'ospfnstop' in line):
					line = (f.readline()).rstrip()
					if not line: break

					if 'Advertising Router' in line:
						extra, router = line.split('Router ', 1)
					# The case matters here and is required. Log files are wierd!
					elif 'name prefix:' in line:
						extra, prefix = line.split('prefix: ', 1)
					elif 'Name Prefix:' in line:
						extra, prefix = line.split('Prefix: ', 1)
					elif 'Update_name_opaque_lsa called' in line:
						action = 'add'
					elif 'Delete _name opaque lsa called' in line:
						action = 'del'

				if router and prefix:
					# Process the action
					if action == 'add':
						router_prefixes[prefix] = router
						prefix_timestamp[prefix] = timestamp
					elif action == 'del' and router_prefixes.has_key(prefix):
						del router_prefixes[prefix]
						prefix_timestamp[prefix] = timestamp

			elif 'router-LSA' in line:
				while (not 'lsa_read called' in line) and (not 'ospfnstop' in line):
					line = (f.readline()).rstrip()
					if not line: break

					if 'Advertising Router' in line:
						extra, router = line.split('Router ', 1)
						router_links[router].clear()
					elif 'Link ID' in line:
						extra, linkID = line.split('Link ID ', 1)
					elif 'Link Data' in line:
						extra, linkdata = line.split('Link Data ', 1)
					elif 'Type' in line:
						extra, _type = line.split('Type ')
						if _type == '1':
							router_links[router].add((linkID, linkdata))

				link_timestamp[router] = timestamp

		lasttimestamp = timestamp
		lastbyte = f.tell()

################
# Update files #
################
with open (localdir + '/prefix', 'w') as f:
	for prefix, router in router_prefixes.items():
		timestamp = prefix_timestamp[prefix]
		f.write(prefix + ':' + router + ':' + timestamp + '\n')

with open (localdir + '/links', 'w') as f:
	linkinfo = set

	for router, linkinfo in router_links.items():
		f.write('Router:' + router + '\n')
		for linkID, linkdata in linkinfo:
			f.write(linkID + ':' + linkdata + '\n')

		f.write('END\n')

with open (localdir + '/link_timestamp', 'w') as f:
	for router, timestamp in link_timestamp.items():
		f.write(router + ':' + timestamp + '\n')

with open (localdir + '/parse.conf', 'w') as f:
	f.write('logdir=' + logdir + '\n')
	f.write('lastfile=' + directory[-1] + '\n')
	f.write('lasttimestamp=' + lasttimestamp + '\n')
	f.write('lastbyte=' + str(lastbyte) + '\n')
	f.write('timezone=' + timezone + '\n')
	end = time.time() - start
	f.write('timetaken=' + str(end) + '\n')
