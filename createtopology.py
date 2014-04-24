#!/usr/bin/python
file = open('topology', 'w')
numNodes = raw_input("How many nodes are in the topology?\n")
nodeIPs = []
for x in xrange(0,int(numNodes)):
	if x == 0:
		while True:
			temp = raw_input("what is the ip of the first node?\n")
			octets = temp.split(".")
			octets = [int(k) for k in octets]
			if len(octets)!= 4 or octets[0] < 1 or octets[0] > 255 or octets[1] < 0 or octets[1] > 255 or octets[2] < 0 or octets[2] > 255 or octets[3] < 0 or octets[3] > 255:
				print "This is not a valid ip address."
			else:
				nodeIPs.append(temp)
				break
	else:
		while True:
			temp = raw_input("what is the ip of the next node?\n")
			octets = temp.split(".")
			octets = [int(k) for k in octets]
			if len(octets)!= 4 or octets[0] < 1 or octets[0] > 255 or octets[1] < 0 or octets[1] > 255 or octets[2] < 0 or octets[2] > 255 or octets[3] < 0 or octets[3] > 255:
				print "This is not a valid ip address."
			elif temp in nodeIPs:
				print "You have already entered that IP please try another."
			else:
				nodeIPs.append(temp)
				break
def printIPs():
	print "ID:IP Address"
	for x in xrange(0,len(nodeIPs)):
		print str(x) + ":" + str(nodeIPs[x])
def writeIPs(neighbors):
	file.write("router:"+ nodeIPs[int(neighbors[0])] + "\n")
	for x in xrange(1,len(neighbors)):
		file.write(nodeIPs[int(neighbors[x])]  + ":Red\n")
	file.write("END\n")
for x in xrange(0,len(nodeIPs)):
	printIPs()
	while True:
		neighborsraw = raw_input("List the nodes that are connected to " + nodeIPs[x] + " using the number from above. eq. 2,3,4.\n")
		neighbors = neighborsraw.split(",")
		#begin input checking
		#prevents the user from entering duplicate values
		if len(neighbors) != len(set(neighbors)):
			print "You entered a node twice please try again."
		#prevents the user from entering the current node in the list of connected nodes
		elif str(x) in neighbors:
			print "We know that the node is connected to itself."
		#prevents the user from entering a node that is not in the list
		elif int(max(neighbors)) > len(nodeIPs)-1 or int(min(neighbors)) < 0:
			print "One of the nodes you entered does not exist."
		else:
			break
	#attached the current node to the front of the array so that
	#writeIPs knows which node to connected the listed IPs to
	neighbors.insert(0,x)
	writeIPs(neighbors)
print "Topology file has been created."






