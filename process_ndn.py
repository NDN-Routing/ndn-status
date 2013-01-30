#!/usr/bin/python
#coding=utf-8

############
# Imports. #
############
import socket
import time
import pyccn
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

###################################
# PyCCN Class to publish content. #
###################################
class ccnput(pyccn.Closure):
        def __init__(self, name, content):
                self.handle = pyccn.CCN()
                self.name = pyccn.Name(name)
                self.content = self.prepareContent(content, self.handle.getDefaultKey())
		self.handle.put(self.content)

        def prepareContent(self, content, key):
                co = pyccn.ContentObject()
                co.name = self.name.appendVersion().appendSegment(0)
                co.content = content

                si = co.signedInfo
                si.publisherPublicKeyDigest = key.publicKeyID
                si.keyLocator = pyccn.KeyLocator(key)
                si.type = pyccn.CONTENT_DATA
                si.finalBlockID = pyccn.Name.num2seg(0)

                co.sign(key)
                return co

	def upcall(self, kind, info):
                if kind != pyccn.UPCALL_INTEREST:
                        return pyccn.RESULT_OK

                self.handle.put(self.content)
                self.handle.setRunTimeout(0)

                return pyccn.RESULT_INTEREST_CONSUMED

        def start(self):
                self.handle.setInterestFilter(self.name, self)

##############################
# Functions to process data. #
##############################
def prefix_json():
	prefixes = set
	tmp = []

	for router in sorted(set_topology.keys()):
		status = 'Online'
		prefixes = router_prefixes[router]

		tmp.append('{"router":"' + router + '",')
		tmp.append('"prefixes":[')

		if not prefixes:
			router_prefixes[router].add('-')
			status = 'Offline'

		for prefix in prefixes:
			if not prefix_timestamp.has_key(prefix):
                                prefix_timestamp[prefix] = '-'

			tmp.append('{"prefix":"' + prefix + '",')
			tmp.append('"timestamp":"' + prefix_timestamp[prefix] + '",')
			tmp.append('"status":"' + status + '"}')
		tmp.append(']}')

	data = ''.join(tmp)
	put = ccnput('/ndn/memphis.edu/netlab/status/prefix', data)
	put.start()

def link_json():
	links = set
	status = ''
	tmp = []

	for router, links in sorted(set_topology.items()):
		if not link_timestamp.has_key(router):
			link_timestamp[router] = '-'
	
		tmp.append('{"router":"' + router + '",')
		tmp.append('"timestamp":"' + link_timestamp[router] + '",')
		tmp.append('"links":[')

		for link in links:
			if topology[router, link] == 'lime':
                        	status = 'Online'
                	elif topology[router, link] == 'Red':
                        	status = 'Offline'
                	elif topology[router, link] == 'skyblue':
                        	status = 'notintopology'

                	if status == 'Online' and float(time.time() - (float(link_timestamp[link]))) > 2400:
                        	status = 'Out-of-date'

			tmp.append('{"link":"' + link + '",')
			tmp.append('"status":"' + status + '"}')
		tmp.append(']}')

	data = ''.join(tmp)
	put = ccnput('/ndn/memphis.edu/netlab/status/link', data)
	put.start()

def process_topo():
	links = set
        
	for router, links in router_links.items():
		for link in links:
			if not topology.has_key((router, link)):
				topology[router, link] = 'skyblue'
			else:
				topology[router, link] = 'lime'

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

with open (localdir + '/links') as f:
        while 1:
                line = (f.readline()).rstrip()
                if not line: break

                if 'Router' in line:
                        extra, router = line.split(':', 1)

			if router not in host_name.keys():
				continue

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

		if link not in host_name.keys():
			continue

		link_name = host_name[link]
		link_timestamp[link_name] = timestamp

process_topo()
prefix_json()
link_json()

