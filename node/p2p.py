# This file is for the peer-to-peer network for nodes to communicate with each other
import requests
import time
import socket
import datetime
from copy import deepcopy
from collections import orderedDict

# peer to peer connection using socket

"""
There are both server and client applications running for a single node so that the node
is capable of both their functionalities.
"""

# efficiently use ports
# https://www.geeksforgeeks.org/50-common-ports-you-should-know/

# get ipv4 of node
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# client node, activated when receiver
# TODO: implement support for multiple server connections to client
class Client:
    def __init__(self, ip: str, port: int, sock=None):
        self.ip = ip
        self.port = port

        # socket for client and server cant be the same
        # don't reuse, because the server socket should be constantly running while the client is not
        if sock == None:
            self.sock = socket.socket()
        else:
            self.sock = sock

    # connect to a node (server)
    def connect(self, host, port=None):
        if port != None:
            self.port = port
        
        self.sock.connect((host, self.port))

    # get the message provided by the server (another node)
    def get_message(self, buff_s=512) -> bytes: # buffer size
        return self.sock.recv(buff_s)

    def stop(self):
        self.sock.stop()

# server node, activated when sender, there will be two nodes running. One for client and, 
# one for server
class Server:
    def __init__(self, ip: str, port: int):
        self.host = ip
        self.sock = socket.socket()
        self.port = port
        self.clients = orderedDict() # active client connections
        self.dead = orderedDict() # dead client connections

    # assign address and port number to socket
    def bind(self, port=None):
        if port != None:
            self.port = port

        self.sock.bind((self.host, self.port))

    # waiting for a client to connect
    def listen(self, tm:int=30): # time in seconds
        self.sock.listen(tm)

    # accept connection
    def accept(self, quiet=False):
        try:
            self.cli, self.addr = self.sock.accept() # accept connection
            time = datetime.datetime.now()
            if self.addr in self.clients:
                del self.clients[self.addr] # delete previous connection with same ip then connect
            self.clients[self.addr] = [time, self.cli]
         except:
            if not quiet:
                print("listening possibly not active")

    # find the active and dead client connections
    def active_clients(self):
        for key, value in self.clients.items():
            try:
                value[1].send(f'{self.host} testing connection passed')
            except:
                del self.clients[value[1]]
                if key in self.dead: # delete previous same client dead connection
                    del self.dead[key]
                self.dead[key] = value
    
    # delete all client history
    def del_history(self):
        self.dead = orderedDict() # reset dead connections
        self.active_clients() # re-calculate the dead connections
        self.dead = orderedDict() # reset dead connections

    # send data to client with specified IP
    def send(data, ip, quiet=False): # ip of where to send
        if not self.clients: # if there are no clients
            if not quiet:
                print("no clients found, scanning for clients...")
            self.listen(10)
            self.accept()
        if not isinstance(data, bytes):
            data = str(data).encode('utf-8') # encode data if not encoded
        if ip in self.clients: # find the designated ip to send message to
            client = self.clients[ip][1]
        else:
            raise ValueError("Wrong receiver IP Address, failed to send data")
        client.send(data) # send the client data

    # TODO: define
    # send data to all connected clients
    def send_all(self, data):
        if not self.clients: # if there are no clients
            if not quiet
                print("no clients found, scanning for clients...")
            self.listen(10)
            self.accept()
        if not isinstance(data, bytes):
            data = str(data).encode('utf-8') # encode data if not encoded
        for ip, value in self.clients.items():
            try:
                value[1].send(data)
            except: # if client connection died
                del self.clients[value[1]]
                if key in self.dead: # delete previous same client dead connection
                    del self.dead[key]
                self.dead[key] = value
                  

    # stop the connection with specified ip address
    def stop(self, ip, quiet=False):
        client = self.clients[ip]
        client[1].close()

        if not quiet: # if quiet don't print
            print(f"-----------CLOSE-CONNECTION-NODE-{client}-----------")
        if ip in self.dead:
            del self.dead[ip] # delete the last dead connection from same ip
        self.dead[ip] = client
        del self.clients[ip]
        
    # TODO: find ip from time connection started
    def ip_from_time():
        pass

    # TODO: find time connection started from ip
    def time_from_ip():
        pass

    # delete server data, stop connections and quit server
    def quit_server(self):
        pass

# TODO: have function to get a list of all nodes. list whether tor is used (only works if bridge not used)
# Peer to Peer network without tor
class P2P:
    INITIAL_PORT = 12345 # netbus unofficial transportation protocol
    __port__ # port index, starting from INITIAL_PORT, subtract from it if stopped. amount of nodes are INITIAL_PORT-port_i
    def __init__(self, debug=False):
        self.ip = get_ip()
        self.sock = socket.socket()
        self.port = None

    def listen(self):
        
        time.sleep(5)

    def connect(host, port=None):
        if port != None:
            self.port = port
        
        self.sock.connect((self.ip, self.port))

    def stop(self):
        self.sock.stop()

x = P2P(True)
x.start()

