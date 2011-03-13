#!/usr/bin/python

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# This program is part of the Mindstab GO server package            #
#                                                                   #
# See http://ai.mindstab.net/ for more information.                 #
#                                                                   #
# Copyright 2007 by Dan Ballard, Robert Hausch, and ai.mindstab.net #
#                                                                   #
# This program is free software; you can redistribute it and/or     #
# modify it under the terms of the GNU General Public License       #
# as published by the Free Software Foundation - version 2.         #
#                                                                   #
# This program is distributed in the hope that it will be           #
# useful, but WITHOUT ANY WARRANTY; without even the implied        #
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR           #
# PURPOSE.  See the GNU General Public License in file COPYING      #
# for more details.                                                 #
#                                                                   #
# You should have received a copy of the GNU General Public         #
# License along with this program; if not, write to the Free        #
# Software Foundation, Inc., 51 Franklin Street, Fifth Floor,       #
# Boston, MA 02111, USA.                                            #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #



from getopt import *
import sys  
import string
import re
import socket
import os
import netpipe
import time
import signal
#for get_ip_address
import fcntl
import struct


debug = 1
house = {}
lastpid = 0

portpool = [10001, 10002, 10003, 10004, 10005, 10006, 10007, 10008, 10009, 10010]
currentport = 0
children = []


#borrowed from the internet
def get_ip_address(ifname):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(
		s.fileno(),
		0x8915,  # SIOCGIFADDR
		struct.pack('256s', ifname[:15])
	)[20:24])


def getnextport():
	global portpool
	global currentport
	port = portpool[currentport]
	currentport = currentport + 1
	if currentport >= len(portpool):
		currentport = 0
	return port

class housebot:
	def __init__(self, np, bot):
		self.np = np
		self.bot = bot

	def getval(self, name):
		val = self.bot[name]
		if val != None:
			return val
		else: 
			return ""

	def setpid(self, pid):
		self.bot[pid] = pid

	def playgame(self, address, port):
		cmd = "play " + address + " " + port 
		self.np.send(cmd)
	
	def cleanup(self):
		self.np.close()

	def quit(self, passwd):
		self.np.send("quit " + passwd)
		resp = self.np.receive()
		return resp == "yes"

	def keepalive(self):
		self.np.send("ping")
		resp = self.np.receive()
		return resp == "pong"

def handleconnection(np):
	global house
	try:
		cmd = np.receive()
	except:
		np.close()
		return
		
	
	cmds = cmd.split(" ")
	if cmds[0] == "house":
		handlehouse(np, cmd[6:])
	elif cmds[0] == "guest":
		handleguest(np, cmds)
	elif cmds[0] == "quit":
		handlequit(cmds)
		np.close()
	elif cmds[0] == "list":
		botlist = ""
		for pid in house.keys():
			botlist = botlist + str(pid) + ","  + house[pid].getval("name") + "," + house[pid].getval("version") + "," + house[pid].getval("author") + "\n"
		np.send(botlist)
		np.close()
	elif cmds[0] == "match":
		handlematch(cmds, np)
		np.close()

def parsebotstr(botstr):
	bot = {}
	for info in botstr.split(","):
		try:
			(opt, val) = info.split("=")
		except:
			continue
		bot[opt] = val
	return bot

def handlehouse(np, botstr):
	hbot = housebot(np, parsebotstr(botstr))
	pid = registerhousebot(hbot)
	np.send("pid " + str(pid))


def registerhousebot(hbot):
	global house
	global lastpid
	house[lastpid] = hbot
	hbot.setpid(lastpid)
	lastpid = lastpid + 1
	return lastpid -1


def removehousebot(pid):
	global house
	house[pid].cleanup()
	del house[pid]

def handlequit(cmds):
	global house
	pid = int(cmds[1])
	if not pid in house.keys():
		return
	passwd = cmds[2]
	if house[pid].getval("password") == passwd:
		if house[pid].quit(passwd):
			removehousebot(pid)
	
def spawngtpserver(port, games):
        global children
	reapchildren()
	pid = os.spawnlp(os.P_NOWAIT, "./gtpserver.py", "./gtpserver.py", "--port", str(port), "--games", games) #, "--sgfbase", "gtpserver") # NO SGF STORING FOR NOW
	# let the server start
	time.sleep(1)
	children.append(pid)
	return pid

def reapchildren():
        global children
	for child in children:
		(pid, exit) = os.waitpid(child, os.WNOHANG)
		if pid != 0:
			children.remove(child)


def abortmatch(pid, botid, np):
	removehousebot(botid)
	os.kill(pid, signal.SIGKILL)
	np.send("error NOID " + str(botid))

def handlematch(cmds, np):
	global house, ip_address
	id1 = int(cmds[1])
	id2 = int(cmds[2])
	if id1 not in house.keys():
		np.send("error NOID " + cmds[1])
		return
	if id2 not in house.keys():
		np.send("error NOID " + cmds[2])
		return
	games = cmds[3]
	port = getnextport()
	pid = spawngtpserver(port, games)
	try:
		house[id1].playgame(ip_address, str(port))
	except:
		print "abort 1"
		abortmatch(pid, id1, np)
		return
	try:
		house[id2].playgame(ip_address, str(port))
	except:
		print "abort 2"
		abortmatch(pid, id2, np)
		return
	np.send("ok")

def handleguest(np, cmds):
	global house, ip_address
	id1 = int(cmds[1])
	if id1 not in house.keys():
		np.send("error NOID " + cmds[1])
		return
	games = cmds[2]
	port = getnextport()
	pid = spawngtpserver(port, games)
	try:
		house[id1].playgame(ip_address, str(port))
	except:
		abortmatch(pid, id1, np)
		return
	np.send("play " + ip_address + " " + str(port))
	


ip_address =  get_ip_address("eth0")
port = 10000

print "'" + ip_address + "'"

def usage():
	print "server.py --port <port>\n"
	sys.exit(1)


try:
	(opts, params) = getopt(sys.argv[1:], "",
                                ["port=",
				])
except:
	usage();

for opt, value in opts:
	if opt == "--port":
		port = value

if port == 0:
	usage()



serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Behave better after crash
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#print socket.gethostname()
#print socket.gethostbyname(socket.gethostname())
serversocket.bind( ('', int(port))) #(socket.gethostname(), int(port)))

def clean_house():
	reapchildren()
	for pid in house.keys():
		try:
	#		print "trying bot[%d] %s\n" % (pid, house[pid].getval('name'))
			if not house[pid].keepalive():
				print "failed keepalive\n"
				removehousebot(pid)
		except:
			print "exception to keepalive\n"
			removehousebot(pid)

serversocket.settimeout(30)
serversocket.listen(2)

while 1:
	try:
		(socket, address) = serversocket.accept()
	except:
		clean_house()
		socket = 0
	if socket:
		np = netpipe.netpipe(socket)
		handleconnection(np)

os.kill(pid, signal.SIGKILL)
closeconnections()
serversocket.close()
