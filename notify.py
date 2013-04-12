#!/usr/bin/python
#coding=utf-8

############
# Imports. #
############
import socket
import smtplib
import time
import sys
import multiprocessing

from email.header import Header
from email.utils import formataddr
from email.mime.text import MIMEText
from collections import defaultdict

##############
# Variables. #
##############
COMMASPACE = ', '
LOCAL_DIR = '/home/ndnmonitor/LogScripts'
FROM = formataddr((str(Header(u'Adam Alyyan', 'utf-8')), 'aalyyan@memphis.edu'))

CC_LIST = []
cc1 = formataddr((str(Header(u'Adam Alyyan', 'utf-8')), 'aalyyan@memphis.edu'))
CC_LIST = [cc1, cc2, cc3, cc4, cc5]

host_name = {}
routers = {}
links	= set()
topology = set()
contact_list = defaultdict(list)

#############################################
# Function to send email, and write to log. #
#############################################
def toLog(message):
        with open(LOCAL_DIR + '/notify.log', 'a') as f:
                _time = time.asctime(time.localtime(time.time()))
                f.write(_time + ' - ' + message + '\n')

def send(router, _type):
	message = []
	
	if isinstance(router, tuple):
		router = router[0]

	toLog('Sending email to: ' + host_name[router])

	message.append('Dear Operator of ' + host_name[router] + ',\n\n')

	if _type == 'prefix':
		message.append('The status page has detected that the prefix')
		message.append(' associated with your node')
		message.append(' is currently not being displayed.\n\n')
		message.append('This message is repeated once every 24 hours until')
		message.append(' the problem is fixed. If you have any questions,')
		message.append(' please contact Adam Alyyan (aalyyan@memphis.edu).\n\n')
		message.append('Link to status page: http://netlab.cs.memphis.edu/script/htm/status.htm\n')
	elif _type == 'link':
		message.append('The status page has detected that your link(s)')
		message.append(' with the following node(s) is/are down:\n')
	
		down = no_link[router]
	
		for link in down:
			message.append('- ' + host_name[link] + '.\n');

		message.append('\nThis message is repeated once every 24 hours until')
                message.append(' the problem is fixed. If you have any questions,')
                message.append(' please contact Adam Alyyan (aalyyan@memphis.edu).\n\n')
                message.append('Link to status page: http://netlab.cs.memphis.edu/script/htm/status.htm\n')

	message = ''.join(message)
	msg = MIMEText(message)

	# Set the header information.
	sendto = contact_list[router]
	SEND_LIST = []
	for element in sendto:
		address = element[0]
		name = element[1]
		toLog('Recipient: ' + name + ', ' + address)
		temp = formataddr((str(Header(name, 'utf-8')), address))
		SEND_LIST.append(temp)

	msg['Subject'] = _type.title() + ' down - ' + host_name[router]
	msg['From'] = FROM
	msg['To'] = COMMASPACE.join(SEND_LIST)
	msg['cc'] = COMMASPACE.join(CC_LIST)

	# Send the email using UoM mail server.
	#s = smtplib.SMTP('localhost')
	#s.sendmail(FROM, SEND_LIST+CC_LIST, msg.as_string())
	s.quit()

	toLog('Email successfully sent to: ' + host_name[router])

##############################
# Function to get host name. #
##############################
def lookup(host, q):
        q.put(socket.gethostbyaddr(host))

#####################################################################
# Open prefix, links, contact list,  and topology file to get data. #
#####################################################################
with open(LOCAL_DIR + '/prefix') as f:
	for line in f:
		line = line.rstrip()
		prefix, router, timestamp = line.split(':', 2)

		routers[router] = prefix

with open(LOCAL_DIR + '/links') as f:
	while 1:
		line = (f.readline()).rstrip()
		if not line: break

		if 'Router' in line:
			extra, router = line.split(':', 1)
			
			while not 'END' in line:
				line = (f.readline()).rstrip()
				if not line: break
				if 'END' in line: break

				link, extra = line.split(':', 1)
				links.add((router, link))

with open(LOCAL_DIR + '/topology') as f:
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

                        while not 'END' in line:
                                line = (f.readline()).rstrip()
                                if not line: break
                                if 'END' in line: break

                                link, extra = line.split(':', 1)
                                topology.add((router, link))

with open(LOCAL_DIR + '/list.txt') as f:
	for line in f:
		contact = []

		line = line.rstrip()
		router, info = line.split('>', 1)
		
		contact = info.split(':')
		contact = zip(contact[0::2], contact[1::2])
		contact_list[router] = contact	

################################################
# Determine which links and prefixes are down. #
################################################
no_link = topology - links
no_link = list(no_link)

temp_routers = routers.keys() 
topo_routers = [x[0] for x in topology]

no_prefix = set(topo_routers) - set(temp_routers)
no_prefix = list(no_prefix)

temp = defaultdict(set)

for node in no_prefix:
	if 'netlogic' in host_name[node] or '141.225.11.150' in node:
		send(node, 'prefix')
		print 'netlogic found. Terminating'
		sys.exit(0)

for router, link in no_link:
	add = True

	for key in no_prefix:
		if key in (router, link):
			add = False
			break
	
	if  add == True: 
		temp[router].add(link)

no_link = temp

####################
# Send out emails. #
####################
with open(LOCAL_DIR + '/notify.log', 'a') as f:
        _time = time.asctime(time.localtime(time.time()))
        f.write(_time + ' - New instance of notify started...\n')

for router in no_prefix:
	send(router, 'prefix')

for router in no_link.keys():
	router = (router, link)
	send(router, 'link')

toLog('Instance ended.\n\n')

