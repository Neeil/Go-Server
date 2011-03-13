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
import os
import netpipe
import socket
import time

debug = 1
children = []

def readbotfile(botfile):
	bot = {}
	file = open(botfile, "r")
	for line in file:
		#line = file.readline()
		line = line.strip("\n")
		if line == "":
			continue
		(opt, value) = line.split("=")
		bot[opt] = value
	file.close()
	if not bot.has_key('handle-net'):
		bot['handle-net'] = 'false'
	return bot

def houseloop(np, bot):
	quit = False
	while not quit:
		cmd = np.receive()
		#print cmd
		cmds = cmd.split(" ")
		#print cmds
		if cmds[0] == "quit":
			#print "cmd == quit"
			#print cmds[1] + " <=> " +  botinfo["password"]
			if cmds[1] == bot["password"]:
				np.send("yes")
				quit = True
			else:
				np.send("no")
		elif cmds[0] == "pid":
			print "ID: " + cmds[1]
		elif cmds[0] == "ping":
			np.send("pong")
		elif cmds[0] == "play":
			address = cmds[1]
			port = cmds[2]
			print "Game accepted @ %s-%s-%s %s:%s:%s\n" % time.localtime()[:6]
			spawnbot(bot["program"], bot["handle-net"], address, port)
			#os.spawnlp(os.P_NOWAIT, "./gtp2ip.py", "./gtp2ip.py", "--program", bot["program"], "--ip", address, "--port", port)
			

def spawnbot(program, handleNet, address, port, feedback = False):
	global children
	reapchildren()
	if handleNet == 'true':
		print "starting wrapper " + program + " " + address + " " +port
		pid = os.spawnlp(os.P_NOWAIT, program, program, address, port)
	elif feedback:
		pid = os.spawnlp(os.P_WAIT, "./gtp2ip.py", "./gtp2ip.py", "--program", program, "--ip", address, "--port", port, "--feedback")
	else:
		pid = os.spawnlp(os.P_NOWAIT, "./gtp2ip.py", "./gtp2ip.py", "--program", program, "--ip", address, "--port", port)
	children.append(pid)
	
def reapchildren():
	global children
	for child in children:
		(pid, exit) = os.waitpid(child, os.WNOHANG)
		if pid != 0:
			children.remove(child)



usagestr = """

goclient.py --server [server name]

	--list				List house bots on server
	--house <botfile>		Register a house bot on the server
	--guest <botfile> --vs <id>	Set your bot to play agaist a house bot
	--quit <id> --pass <pass>	Remove one of your house bots from the server
	--match <id> --vs <id>		Play two house bots against each other
		[--games <number>]	... for number of games

	--ip
	--port

"""


port = "10000"
ip = ""
botfile = ""
cmd = ""
vs = ""
passwd = ""
pid = "0"
match = "0"
games = "1"
server = ""

def usage():
	global usagestr
	print usagestr 
	sys.exit(1)


try:
	(opts, params) = getopt(sys.argv[1:], "",
                                ["port=",
				 "ip=",
				 "server=",
				 "list",
				 "house=",
				 "guest=",
				 "vs=",
				 "quit=",
				 "pass=",
				 "match=",
				 "games=",
				])
except:
	usage()

for opt, value in opts:
	if opt == "--port":
		port = value
	elif opt == "--ip":
		ip = value
	elif opt == "--server":
		server = value
		ip = socket.gethostbyname(server)
	elif opt == "--list":
		cmd = "list"
	elif opt == "--house":
		cmd = "house"
		botfile = value
	elif opt == "--guest":
		cmd = "guest"
		botfile = value
	elif opt == "--quit":
		cmd = "quit"
		pid = value
	elif opt == "--vs":
		vs = value
	elif opt == "--pass":
		passwd = value
	elif opt == "--match":
		cmd = "match"
		match = value
	elif opt == "--games":
		games = value


if port == 0 or ip == "" or cmd == "" or (cmd == "guest" and vs == "") or (cmd == "match" and vs == ""):
	usage()


np = netpipe.netpipe()
np.connect(ip,int(port))

if cmd == "list":
	np.send("list")
	list = np.receive()
	print "ID\tName\t\tVersion\t\tAuthor"
	for botstr in list.split("\n"):
		if botstr == "":
			continue
		(pid,name,version,author) = botstr.split(",")
		print "%s\t%s\t\t%s\t\t%s" % (pid,name,version,author)
elif cmd == "house":
	bot = readbotfile(botfile)
	botinfo = ""
	for opt in bot.keys() :
		botinfo = botinfo + opt + "=" + bot[opt] +","
	np.send("house " + botinfo)
	houseloop(np, bot)
elif cmd == "quit":
	np.send("quit " + pid + " " + passwd)
elif cmd == "match":
	np.send("match " + match + " " + vs + " " + games)
	resp = np.receive()
	print resp
elif cmd == "guest":
	bot = readbotfile(botfile)
	np.send("guest " + vs + " " + games)
	resp = np.receive()
	resps = resp.split(" ")
	if resps[0] == "error":
		print resps
	elif resps[0] == "play":
		spawnbot(bot["program"], bot["handle-net"], resps[1], resps[2], True)


np.close()
