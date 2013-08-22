# Email script for ndn status test bed
#
# Sends out emails to operators of nodes which are offline, or when links are down. This script
# uses PyCCN to retrieve the status content that is published under the following names:
#
#	o /ndn/memphis.edu/netlab/status/prefix
#	o /ndn/memphis.edu/netlab/status/link
#
# The SingleSlurp class is based off the slurp example provided with PyCCN.
#
# Author: Adam Alyyan

# Imports
import sys
import pyccn
import json
import socket
import smtplib

from email.header import Header
from email.utils import formataddr
from email.mime.text import MIMEText

# Globals
TEST = True

prefixRaw = ''
linkRaw = ''

fPrefix = []
fLink = []

nodesDown = []
linksDown = {}

contact = {}

commaspace = ', '
sender = formataddr((str(Header(u'Adam Alyyan', 'utf-8')), 'aalyyan@memphis.edu'))

cc0 = formataddr((str(Header(u'Adam Alyyan', 'utf-8')), 'aalyyan@memphis.edu'))
#cc1 = formataddr((str(Header(u'Lan Wang', 'utf-8')), 'lanwang@memphis.edu'))
#cc2 = formataddr((str(Header(u'Obaid Syed', 'utf-8')), 'obaidsyed@gmail.com'))
#cc3 = formataddr((str(Header(u'A K M Mahmudul Hoque', 'utf-8')), 'ahoque1@memphis.edu')) 
cc = [cc0]#, cc1, cc2, cc3]

# Special cases for emails
sppnodes = ['sppatla1.arl.wustl.edu', 'spphous1.arl.wustl.edu', 'sppkans.arl.wustl.edu', 'sppsalt1.arl.wustl.edu', 'sppwash1.arl.wustl.edu']

# Retrieves the latest content under the root namespace
class SingleSlurp(pyccn.Closure):
	def __init__(self, root, handle = None):
		self.root = pyccn.Name(root)
		self.exclusions = pyccn.ExclusionFilter()
		self.handle = handle or pyccn.CCN()

	def start(self, timeout):
		self.exclusions.reset()
		self.express_my_interest()
		self.handle.run(timeout)

	def express_my_interest(self):
		templ = pyccn.Interest(exclude = self.exclusions, childSelector = 1)
		self.handle.expressInterest(self.root, self, templ)

	def upcall(self, kind, upcallInfo):
		if kind == pyccn.UPCALL_FINAL:
			return pyccn.RESULT_OK

		if kind == pyccn.UPCALL_INTEREST_TIMED_OUT:
			print("Got timeout!")
			return pyccn.RESULT_OK

		# make sure we're getting sane responses
		if not kind in [pyccn.UPCALL_CONTENT, pyccn.UPCALL_CONTENT_UNVERIFIED, pyccn.UPCALL_CONTENT_BAD]:
			print("Received invalid kind type: %d" % kind)
			sys.exit(100)

		#matched_comps = upcallInfo.matchedComps
		response_name = upcallInfo.ContentObject.name
		content = upcallInfo.ContentObject.content
		
		if ('prefix' in response_name):
			global prefixRaw
			prefixRaw = content
		else:
			global linkRaw
			linkRaw = content

		return pyccn.RESULT_OK

def prepPrefix(element):
	message = []

	if isinstance(element, list):
		to = ''
		print element
		for i in element:
			to += (i + ', ')
		
		print to
		message.append('Operator of: ' + to + '\n\n')
	else:
		message.append('Operator of: ' + element + ',\n\n')

	message.append('The status page has detected that your node(s) are currently offline, and no prefix is being displayed.\n\n')
	message.append('Status: http://netlab.cs.memphis.edu/script/htm/status.htm\n\n');
	message.append('This message repeats once every 24 hours until the issue is resolved. If you have any questions, or believe you incorrectly received this alert, please contact Adam Alyyan (aalyyan@memphis.edu)');
	
	message = ''.join(message)
	email = MIMEText(message)

	return email

def send(email, element):
	# Get the contact information
	if isinstance(element, list):
		recipient = contact[element[0]]
	else:
		recipient = contact[element]

	# Set the final recipients
	send = []
	
	if TEST:
		send.append(formataddr((str(Header(u'Adam Alyyan', 'utf-8')), 'aalyyan@memphis.edu')))
	else:
		for i in recipient:
			send.append(formataddr((str(Header(i[1], 'utf-8')), i[0])))

	# Set headers
	email['Subject'] = 'NDN Status Alert - Node  offline'
	email['From'] = sender
	email['To'] = commaspace.join(send)
	email['cc'] = commaspace.join(cc)

	s = smtplib.SMTP('mta.memphis.edu', 25)
	#s.sendmail(sender, send + cc, email.as_string())
	s.quit()
	

def openList():
	with open('list.txt', 'r') as f:
		global contact

		for line in f:
			tmp = []
		
			line = line.rstrip()
			router, info = line.split('>', 1)
	
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
				try:
					res = socket.gethostbyaddr(router)
					router_name = res[0]
				except:
					router_name = router

			tmp = info.split(':')
			tmp = zip(tmp[0::2], tmp[1::2])
			contact[router_name] = tmp

# Takes in the raw status information which is delimited by 'END', and converts it back into
# pure json
def parseJson(s, l):
	data = s.split('END')

	for i in data:
		l.append(json.loads(i))


# Main

# Get the status information for prefixes
ss = SingleSlurp('/ndn/memphis.edu/netlab/status/prefix')
ss.start(500)

# Get the status information for links
ss = SingleSlurp('/ndn/memphis.edu/netlab/status/link')
ss.start(500)

# Convert the data into readable/workable json
parseJson(prefixRaw, fPrefix)
parseJson(linkRaw, fLink)

# Core logic. If a node is offline, it is appended to the 'nodesDown' list. If a link is down, a check
# occurs to see if the node is in the 'nodesDown' list. If so, we continue and ignore it. If not, we
# cycle through the links for that node and check for offline ones. If the link node is already in
# the 'nodesDown' list, we ignore it, else it is added to a 'tmp' list. After cycling through the links,
# if the length of 'tmp' is greater than 0, we add it to the 'linksDown' list with the nodes parent as 
# the key

# Cycle through the prefixes and find the offline nodes
tmp = []
for line in fPrefix:
	if 'Offline' in line['prefixes'][0]['status']:
		if line['router'] in sppnodes:
			tmp.append(line['router'])
		else:
			nodesDown.append(line['router'])

if len(tmp) > 0:
	nodesDown.append(tmp)

# Cycle through the links and find which links are down (ignoring where nodes are offline)
for line in fLink:
	tmp = []

	# If it is already in nodesDown, skip the rest
	if line['router'] in nodesDown:
		continue

	for link in line['links']:
		# If it's offline and not in nodesDown, add to the list
		if 'Offline' in link['status'] and link['link'] not in nodesDown: 
			tmp.append(link['link'])

	# If we have links down, add the list to the linksDown table
	if len(tmp) > 0:
		linksDown[line['router']] = tmp

openList()

print nodesDown

for i in nodesDown:
	email = prepPrefix(i)
	send(email, i)


