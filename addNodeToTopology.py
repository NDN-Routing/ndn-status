import sys
import os
yes = 'yes'
cont = raw_input("This script can be used to add a new node to the topology. Would you like to continue?(yes/no)\n")
if cont.lower() != yes:
  sys.exit()

newNodeIP = raw_input("What is the IP of the node you want to add?\n")
numNeighbors = raw_input("How many nodes is it connected to?\n")
neighborsIPs = []
for x in xrange(0,int(numNeighbors)):
	while True:
			temp = raw_input("what is the ip of the next neighbor?\n")
			octets = temp.split(".")
			octets = [int(k) for k in octets]
			if len(octets)!= 4 or octets[0] < 1 or octets[0] > 255 or octets[1] < 0 or octets[1] > 255 or octets[2] < 0 or octets[2] > 255 or octets[3] < 0 or octets[3] > 255:
				print "This is not a valid ip address."
			elif temp in neighborsIPs:
				print "You have already entered that IP please try another."
			else:
				print 'adding to array ' + temp
				neighborsIPs.append(temp)
				break
file = open('topology', 'a')
file.write('router:' + newNodeIP + '\n')
for x in xrange(0,int(numNeighbors)):
	print 'writing to file ' + neighborsIPs[x]
	file.write(neighborsIPs[x] +':Red\n')
file.write('END\n')


for n in xrange(0,int(numNeighbors)):
	top = []
	with open('topology') as f:
		for line in f:
			top.append(line)
	with open('topology', 'w') as f:
		for line in top:
			if 'router:' + neighborsIPs[n] in line:
				f.write(line + newNodeIP + ':Red\n' )
			else:
				f.write(line)
os.system('rm links')
os.system('touch links')
os.system('rm link_timestamp')
os.system('touch link_timestamp')
os.system('rm prefix')
os.system('touch prefix')
