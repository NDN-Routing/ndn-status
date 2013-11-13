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
from pprint import pprint

start = time.time()

################################################
# Delcaring and initializing needed variables. #
################################################
localdir = '/home/ndnmonitor/tmp/ndn-status'
pubprefix = '/ndn/memphis.edu/netlab/status'

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
				timestamp = prefix_timestamp[prefix]

			publish.append('{"prefix":"' + prefix + '",')
			publish.append('"timestamp":"' + timestamp + '",')
			publish.append('"status":"' + status + '"}')
			publish.append(',')

		del publish[-1]
		publish.append(']}')
		publish.append('END')
	del publish[-1]

	data = ''.join(publish)
	put = ccnput("/".join([pubprefix, 'prefix']), data)
	put.start()
	del publish[:]

def to_search():
	links = set
	for router, links in set_topology.items():
		for link in links:
			if topology[router, link] == 'Red':
				router_links[router].add(link)
	return router_links

def link_json():
	links = set
	status = ''
	search = to_search()
	
	for router, links in sorted(search.items()):
		if not link_timestamp.has_key(router):
			timestamp = '-'
		else:
			timestamp = link_timestamp[router]
	
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

			publish.append('{"link":"' + link + '",')
			publish.append('"status":"' + status + '"}')
			publish.append(',')

		del publish[-1]
		publish.append(']}')
		publish.append('END')
	del publish[-1]

	data = ''.join(publish)
        put = ccnput("/".join([pubprefix, 'link']), data)
        put.start()
        del publish[:]

def process_topo():
	links = set
        
	for router, links in router_links.items():
		for link in links:
			if not topology.has_key((router, link)):
				print router, link
				topology[router, link] = 'skyblue'
			else:
				topology[router, link] = 'lime'

#############################################################################################
# Read the configuration file to find the last file timestamp, last timestamp 
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

		if 'timetaken' in line:
			keyword, value = line.split('=', 1)
			timetaken = value
			continue

curtime = time.asctime(time.localtime(time.time()))
timestamp = time.asctime(time.localtime(float(lasttimestamp)))

publish.append('{"lastlog":"' + lastfile + '",')
publish.append('"lasttimestamp":"' + timestamp + '",')
publish.append('"lastupdated":"' + curtime + '"}')
data = ''.join(publish)
put = ccnput("/".join([pubprefix, 'metadata']), data)
put.start()
del publish[:]


######################################################
# Read in prefixes, links, timestamps, and topology. #
######################################################
socket.setdefaulttimeout(5)

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
				q = multiprocessing.Queue()
				p = multiprocessing.Process(target=lookup, args=(router, q))
				p.start()
				p.join(1)
				
				if p.is_alive:
					p.terminate()
					p.join()
				
				if not q.empty():
                                        router_name = (q.get())[0]
                                else:
                                        router_name = router

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

		if router not in host_name.keys():
			router_name, extra1, extra2 = socket.gethostbyaddr(router)
			host_name[router] = router_name
		else:
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

				if linkID not in host_name.keys():
					link_name, extra1, extra2 = socket.gethostbyaddr(linkID)
					host_name[linkID] = link_name
				else:
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
publish.append("\n")
link_json()

print 'Completed'
