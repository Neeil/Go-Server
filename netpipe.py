import socket

class netpipe:
        '''NetPipe: Sends data from one place to another'''
          
        def __init__(self, sock=None):
            if sock is None:
                self.sock = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
            else:
                self.sock = sock
        
	def connect(self, host, port):
            self.sock.connect((host, port))
        
	def send(self, msg):
	    msg =  ("%04d" % len(msg)) + msg
	    #print "np->: "+msg
	    totalsent = 0
            while totalsent < len(msg):
            	sent = self.sock.send(msg[totalsent:])
                if sent == 0:
                    raise SocketClosed, "socket connection broken"
                totalsent = totalsent + sent

        def receive(self):
	    length = int(self.sock.recv(4))
            msg = ''
            while len(msg) < length:
		    line = self.sock.recv(length - len(msg))
	            if line == '':
        	            raise SocketClosed, "socket connection broken"
		    msg = msg + line
		    #print "np<-: " + msg
            return msg
        
	def close(self):
                self.sock.close()
