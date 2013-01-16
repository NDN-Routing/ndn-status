#!/usr/lib/python
#coding=utf-8

COMMASPACE = ', '
CC_list = ['you@cc_list.com', 'me@cc_list.com']

############
# Imports. #
############
import socket
import smtplib

from email.mime.text import MIMEText
from collections import defaultdict

####################################
# Initial variables to store data. #
####################################
host_name = {}
routers = {}

links	= set()
topology = set()

contact_list = defaultdict(list)

###########################
# Function to send email. #
###########################
def send(router, _type):
	message = []
	
	if isinstance(router, tuple):
		router = router[0]

	router = host_name[router]

	message.append('Dear Operator of ' + router + ',\n\n')

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
		message.append(' with the following links is/are down:\n')
	
		down = no_link[router]

		for link in down:
			message.append('- ' + link + '.\n');

		message.append('\nThis message is repeated once every 24 hours until')
                message.append(' the problem is fixed. If you have any questions,')
                message.append(' please contact Adam Alyyan (aalyyan@memphis.edu).\n\n')
                message.append('Link to status page: http://netlab.cs.memphis.edu/script/htm/status.htm\n')
	
	message = ''.join(message)
	msg = MIMEText(message)

	# Set the header information.
	msg['Subject'] = 'Subject here'
	msg['From'] = 'me@pythoniscool.com'
	msg['To'] = 'aalyyan@memphis.edu'
	msg['CC'] = COMMASPACE.join(cc_list)

	# Send the email using UoM mail server.
	#s = smtplib.SMTP('localhost')
	#s.sendmail(msg['From'], msg['To'], msg.as_string())
	#s.quit()

#####################################################################
# Open prefix, links, contact list,  and topology file to get data. #
#####################################################################
with open('prefix') as f:
	for line in f:
		line = line.rstrip()
		prefix, router, timestamp = line.split(':', 2)

		routers[router] = prefix

with open('links') as f:
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

with open('topology') as f:
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

                        while not 'END' in line:
                                line = (f.readline()).rstrip()
                                if not line: break
                                if 'END' in line: break

                                link, extra = line.split(':', 1)
                                topology.add((router, link))

with open('list.txt') as f:
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

for router, link in no_link:
	add = True

	for key in no_prefix:
		if key in (router, link):
			add = False
			break
	
	if  add == False: 
		temp[router].add(link)

no_link = temp

####################
# Send out emails. #
####################
for router in no_prefix:
	send(router, 'prefix')

for router in no_link.keys():
	router = (router, link)
	send(router, 'link')
