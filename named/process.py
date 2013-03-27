#!/usr/bin/python
#coding=utf-8

############
# Imports. #
############
import socket
import time
import pyccn
import multiprocessing
from collections import defaultdict

################################################
# Delcaring and initializing needed variables. #
################################################
localdir = '/home/ndnuser/ndn-status/named'

links_list = []
publish = []

prefix_timestamp = {}
link_timestamp = {}
host_name = {}
topology  = {}

set_topology = defaultdict(set)
router_links  = defaultdict(set)
router_prefixes	= defaultdict(set)

#####################
# Timeout function. #
#####################
def lookup(host, q):
	q.put(socket.gethostbyaddr(host))

###################################
# PyCCN Class to publish content. #
###################################

class ccnput(pyccn.Closure):
        def __init__(self, name, content):
                c = pyccn.CCN()
		c.setRunTimeout(60000)
		self.handle = c
		#self.handle = pyccn.CCN()
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

                self.handle.put(self.content) # send the prepared data
                self.handle.setRunTimeout(0) # finish run() by changing its timeout to 0

                return pyccn.RESULT_INTEREST_CONSUMED

        def start(self):
		pass
                # register our name, so upcall is called when interest arrives
                #self.handle.setInterestFilter(self.name, self)

##############################
# Functions to process data. #
##############################
def prefix_json():
	prefixes = set
	search = list(set(set_topology.keys()) | set(router_prefixes.keys()))

	for router in sorted(search):
		status = 'Online'
		prefixes = router_prefixes[router]

		publish.append('{"router":"' + router + '",')
		publish.append('"prefixes":[')

		if not prefixes:
			router_prefixes[router].add('-')
			status = 'Offline'

		if router not in set_topology.keys():
			status = 'notintopology'

		for prefix in prefixes:
			if not prefix_timestamp.has_key(prefix):
                                timestamp = '-'
			else:
				timestamp = time.asctime(time.localtime(float(prefix_timestamp[prefix]))) + ' ' + timezone

			publish.append('{"prefix":"' + prefix + '",')
			publish.append('"timestamp":"' + timestamp + '",')
			publish.append('"status":"' + status + '"}')
			publish.append(',')

		del publish[-1]
		publish.append(']}')
		publish.append('END')
	del publish[-1]

	data = ''.join(publish)
	put = ccnput('/ndn/memphis.edu/internal/status/prefix', data)
	put.start()
	del publish[:]
	print data

def link_json():
	links = set
	status = ''
	search = dict(router_links.items() + set_topology.items())

	for router, links in sorted(search.items()):
		if not link_timestamp.has_key(router):
			timestamp = '-'
		else:
			timestamp = time.asctime(time.localtime(float(link_timestamp[router]))) + ' ' + timezone
	
		publish.append('{"router":"' + router + '",')
		publish.append('"timestamp":"' + timestamp + '",')
		publish.append('"links":[')

		for link in links:
			if topology[router, link] == 'lime':
                        	status = 'Online'
                	elif topology[router, link] == 'Red':
                        	status = 'Offline'
                	elif topology[router, link] == 'skyblue':
                        	status = 'notintopology'

                	if status == 'Online' and float(time.time() - (float(link_timestamp[link]))) > 2400:
                        	status = 'Out-of-date'

			publish.append('{"link":"' + link + '",')
			publish.append('"status":"' + status + '"}')
			publish.append(',')

		del publish[-1]
		publish.append(']}')
		publish.append('END')
	del publish[-1]

	data = ''.join(publish)
        put = ccnput('/ndn/memphis.edu/internal/status/link', data)
        put.start()
        del publish[:]
	print data

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

curtime = time.asctime(time.localtime(time.time())) + ' ' + timezone
timestamp = time.asctime(time.localtime(float(lasttimestamp))) + ' ' + timezone

publish.append('{"lastlog":"' + lastfile + '",')
publish.append('"lasttimestamp":"' + timestamp + '",')
publish.append('"lastupdated":"' + curtime + '"}')
data = ''.join(publish)
put = ccnput('/ndn/memphis.edu/internal/status/metadata', data)
put.start()
del publish[:]


######################################################
# Read in prefixes, links, timestamps, and topology. #
######################################################
with open (localdir + '/topology') as f:
        while 1:
                line = (f.readline()).rstrip()
                if not line: break

                if 'Router' in line:
                        extra, router = line.split(':', 1)

                        while not 'END' in line:
                                line = (f.readline()).rstrip()
                                if not line: break
                                if 'END' in line: break

                                adj_router, status = line.split(':', 1)
				set_topology[router].add(adj_router)
                                topology[router, adj_router] = status

with open (localdir + '/prefix') as f:
        for line in f:
                line = line.rstrip()
                if not line: break

                prefix, router, timestamp = line.split(':', 2)
                router_prefixes[router].add(prefix)
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

                                link = line
				router_links[router].add(link)

with open (localdir + '/link_timestamp') as f:
	for line in f:
		line = line.rstrip()
		if not line: break

		link, timestamp = line.split(':', 1)
		link_timestamp[link] = timestamp

process_topo()
prefix_json()
publish.append("\n")
link_json()

print 'Completed'

