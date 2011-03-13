#!/usr/bin/python

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# This program is part of the Mindstab GO server package            #
#                                                                   #
# See http://ai.mindstab.net/ for more information.                 #
#                                                                   #
# Copyright 2007 by Dan Ballard, Robert Hausch, and ai.mindstab.net #
#                                                                   #
# Uses GTP_connection class from GnuGo so licenced under GPL3       #
# Origional licence below                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# This program is distributed with GNU Go, a Go program.            #
#                                                                   #
# Write gnugo@gnu.org or see http://www.gnu.org/software/gnugo/     #
# for more information.                                             #
#                                                                   #
# Copyright 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006 and 2007 #
# by the Free Software Foundation.                                  #
#                                                                   #
# This program is free software; you can redistribute it and/or     #
# modify it under the terms of the GNU General Public License       #
# as published by the Free Software Foundation - version 3,         #
# or (at your option) any later version.                            #
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
import socket
import popen2
import sys
import netpipe
import re
import os

debug = 0
#print "%s gtp2ip.py" % (os.getpid())

class GTP_connection:

    def __init__(self, command):
        try:
            infile, outfile = popen2.popen2(command)
        except:
            print "popen2 failed"
            sys.exit(1)
        self.infile  = infile
        self.outfile = outfile

    def exec_cmd(self, cmd):
        global debug
	global feedback

        if debug:
            sys.stderr.write("GTP command: " + cmd + "\n")
	if feedback:
		#if cmd[0:4] == "play":
			print cmd
	if cmd == "protocol_version":
		result = "= gtp2ip-0.1\n"
	elif cmd[0:10] == "game_score":
		if feedback: 
			print "Game Score: " + cmd[10:]
		result = "= \n"
	else:		
		try: 
			self.outfile.write(cmd + "\n\n")
        		self.outfile.flush()
        		result = ""
        		line = self.infile.readline()
			if line == "":
				print "ERROR: bot crashed"
				return "quit\n"
        		while line != "\n":
        		    result = result + line
        		    line = self.infile.readline()
		except:
			print "ERROR: bot crashed"
			return "quit"
        if debug:
            sys.stderr.write("Reply: '" + result + "'\n")
	if feedback:
		#if line[0:4] == "play":
			print result

	return result



def usage():
	print "gtp2ip.py --program '<program command>' --ip <server ip> --port <server port>\n\n"
	sys.exit(1)


program = ""
port = 0
ip = 0
feedback = False

#print sys.argv

try:
	(opts, params) = getopt(sys.argv[1:], "",
                                ["program=",
				 "port=",
				 "ip=",
				 "feedback",
				])
except: 
	print "except error"
	usage()


for opt, value in opts:
	if opt == "--program":
    		program = value
	elif opt == "--port":
		port = value
	elif opt == "--ip":
		ip = value
	elif opt == "--feedback":
		feedback = True

if program == "" or ip == 0 or port == 0:
	usage()


gtp = GTP_connection(program)
#print "GTP active"
np = netpipe.netpipe()
np.connect(ip,int(port))
#print "np active"

while 1:
	try: 
		cmd = np.receive()
	except:
		print "ERROR: socket error"
		sys.exit(-1)
	result = gtp.exec_cmd(cmd)
	if result == "quit":
		np.close()
		sys.exit(-1)
	try:
		np.send(result)
	except: 
		print "ERROR: socket error"
		sys.exit(-1)
	if cmd == 'quit':
		np.close()
		sys.exit(0)

