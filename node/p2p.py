#!/usr/bin/python
from collections import OrderedDict, deque
from copy import deepcopy
from sys import platform
import time
import socket
import datetime
import secrets
import multiprocessing
import threading
import json
import os
import signal
import subprocess

if platform == "linux" or "unix" or "darwin":
    from psutil import process_iter

# This file is for the peer-to-peer network for nodes to communicate with each other
# peer to peer connection using socket

"""
There are both server and client applications running for a single node so that the node
is capable of both their functionalities.
"""


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
        self.client = True

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
        self.clients = OrderedDict() # active client connections
        self.dead = OrderedDict() # dead client connections
        self.client = False
        self._listen_ = False

    # assign address and port number to socket
    def bind(self, port=None):
        if port != None:
            self.port = port

        print("server.bind():", self.host, self.port)
        self.sock.bind((self.host, self.port))

    # waiting for a client to connect
    def listen(self, tm=5): # backlog
#        if isinstance(tm, int):
#            self.sock.listen(tm)
#        else: # boolean
#            self._listen_ = tm
#            while self._listen_:
#                self.sock.listen(5)
#                raise Exception("stopped listening, handling required")
        self.sock.listen(tm)

    # accept connection
    def accept(self, debug=True):
        try:
            self.cli, self.addr = self.sock.accept() # accept connection
            self.addr = self.addr[0]
            time = datetime.datetime.now()
            if self.addr in self.clients:
                del self.clients[self.addr] # delete previous connection with same ip then connect
            self.clients[self.addr] = [time, self.cli, self.port]
            return self.cli, self.addr
        except OSError as e:
            if debug:
                print("failed to accept, ip and port probably not binded\n", e)

    # find the active and dead client connections
    def active_clients(self):
        for key, value in self.clients.items():
            try:
                value[1].send(f'{self.host} testing connection passed')
            except:
                del self.clients[key]
                if key in self.dead: # delete previous same client dead connection
                    del self.dead[key]
                self.dead[key] = value
    
    # delete all client history
    def del_history(self):
        self.dead = OrderedDict() # reset dead connections
        self.active_clients() # re-calculate the dead connections
        self.dead = OrderedDict() # reset dead connections

    # send data to client with specified IP
    def send(self, data, ip, debug=True): # ip of where to send
        if not self.clients: # if there are no clients
            if debug:
                print("no clients found, scanning for clients...")
            self.listen(9)
            self.accept()
        if not isinstance(data, bytes):
            data = str(data).encode('utf-8') # encode data if not encoded
        if ip in self.clients: # find the designated ip to send message to
            client = self.clients[ip][1]
        else:
            raise ValueError(f"Wrong receiver IP Address, failed to send data")
        client.send(data) # send the client data

    # send data to all connected clients
    def send_all(self, data, debug=True):
        if not self.clients: # if there are no clients
            if debug:
                print("no clients found, scanning for clients...")
            self.listen(10)
            self.accept()
        if not isinstance(data, bytes):
            data = str(data).encode('utf-8') # encode data if not encoded
        for key, value in self.clients.items():
            try:
                value[1].send(data)
            except: # if client connection died
                del self.clients[key]
                if key in self.dead: # delete previous same client dead connection
                    del self.dead[key]
                self.dead[key] = value
                  

    # stop the connection with specified ip address
    def stop(self, ip, debug=True):
        client = self.clients[ip]
        client[1].close()

        if debug: # if quiet don't print
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
        for addr, cli_tm in self.clients.items():
            cli_tm[1].close()
        self.clients = OrderedDict()
        self.dead = OrderedDict()

# TODO: have function to get a list of all nodes. list whether tor is used (only works if bridge not used)
# Peer to Peer network without tor
class P2P:
    def __init__(self, port=1025, debug=False):
        self.debug = debug
        self.ip = get_ip()
        # nodes = # [{address: [time, client, port]}] which is self.server.clients
        self.port = port # last used port

        # inititalize ports and client and server connections
        port = self.port
        self.server = Server(self.ip, port)
        port = self.gen_port()
        self.client = Client(self.ip, port)
        ### The client port will be server.port-1 for every node

        # change port of client and server by changing self.xxx.port = rand_port()

    # generate random port if port 8333 is already in use
    def gen_port(self):
        #    port = secrets.randbelow(65536) # randomly generate port
        #    while port in self.used_ports:
        #        port = secrets.randbelow(65536) # randomly generate port
        if self.server.clients: # if there are clients. increase it, otherwise, go to initial value
            self.port+=1
        else:
            self.port = 1025
        port = self.port
        return port

    # listen to nodes
    def listen(self, tm=5):
        self.server.listen(tm)

        # create new thread for listening
        #self.thread = multiprocessing.Process(target=self.server.listen,args=[tm])
        #self.thread.start()
        #self.thread.join()


    # receive the sent data (bytes, not files)
    def receive(self, buff_size=None) -> bytes:
        if buff_size == None:
            buffer = b''
            try:
                while True: # problem here ######################################################################################################################################################
                    chunk = self.client.get_message(128) # receive bytes until there are none to receive
                    if not chunk:
                        break
                    buffer += chunk
            except OSError:
                raise Exception
        else:
            buffer = self.client.get_message(buff_size)
        return buffer

    # bind server with new port
    def bind(self, port):
        try:
            self.server.bind(port)
        except OSError as e: # if address is already binded
            print("address is already binded, continuing...\nerror_msg:", e)
            print("terminating port usage and retrying...")
            if platform == "linux" or platform == "unix" or platform == "darwin":
                c = subprocess.Popen(f"lsof -i tcp:8333", shell=True, # fuser {port}/tcp
                                     stdout=subprocess.PIPE, stderr = subprocess.PIPE)
                stdout, stderr = c.communicate()
                l = stdout.decode().strip().split(' ')
                l = [i for i in l if i]
                if l != []:
                    print('port PID ', l)
                    pid = int(l[0])
                    os.kill(pid, signal.SIGTERM)
                    self.server.bind(port)
                else: # if socket state = TIME_WAIT
                    while True:
                        try:
                            time.sleep(5)
                            print("trying...", end=' ')
                            self.server.bind(port)
                            print("sucess!!!")
                            break
                        except OSError: # address already in use
                            pass

            elif platform == "win32": # if inferior operating system
                subpr = subprocess.Popen(f"netstat -ano|findstr {port}", shell=True, 
                                         stdout=subprocess.PIPE, stderr = subprocess.PIPE)
                stdout, stderr = subpr.communicate()
                try:
                    pid = int(stdout.decode().strip().split(' ')[-1])
                    os.kill(pid, signal.SIGTERM)
                except OSError as e: # address already in use
                    print("error_msg:", e)
                    while True:
                        try:
                            time.sleep(5)
                            print("trying...", end=' ')
                            self.server.bind(port)
                            print("sucess!!!")
                            break
                        except OSError: # address already in use
                            pass
            else:
                raise OSError(f"os: {platform}\tos not recognized")


    # try to connect to other p2p node, connect self.client to other.server
    def connect(self, ip, port, tm=5):
        self.client.port=port

        timer = time.time()+tm
        while True:
            try:
                if time.time() > timer: # try connection for tm seconds.
                    break
                try:
                    self.client.connect(ip, self.client.port)
                except OSError as e: # Transport endpoint is already connected
                    print("error_msg (OSError):", e)
                    break ############### HANDLE PROPERLY
            except ConnectionRefusedError as e: # refused connection
                print("error_msg (ConnectionRefusedError):", e)

    # let server-side of node accept connection
    def accept(self):
        return self.server.accept(self.debug)

    # disconnect with specified node
    def disconnect(self, ip):
        self.server.stop(ip, self.debug)

    # server-side sends data.
    def send(self, data, ip):
        self.server.send(data, ip, self.debug)
    
    # server-side sends data to all clients
    def send_all(self, data):
        self.server.send_all(data)

    # initalize server side from scratch
    def sender(self, port=8333, tm=True):
        self.port=port
        self.bind(port)
        self.listen(tm)

        if platform == "win32": # if inferior os
            self.add_node(port, os.path.abspath('node\\nodes.json')) # windows requires path
        else:
            self.add_node()
    
    # initialize client side from scratch
    def receiver(self, ip, port, buffsize=None, values=None): # buffsize can be custom for efficiency but isn't required
        self.connect(ip, port)
        if values != None:
            values.put(self.receive(buffsize))
        else:
            return self.receive(buffsize)

    # add node to network by adding it to nodes.json
    # send nodes.json after connection so that every node knows which ports are open for which IPs
    def add_node(self, port=8333, filename='nodes.json'): # TODO: remove node from nodes.json when closed, or when active_clients() fails
        with open(filename,'r+') as file:
            data = json.load(file)
            value = {"ip": self.ip, "port": self.port}
            if value not in data["nodes"]: # add if same ip address with same port doesn't exist
                data["nodes"].append(value)
                file.seek(0)
                json.dump(data, file, indent=4)

    def quit(self):
        pass

# TODO: create new socket for each client, the only way to not terminate client connection after sending message.
# maybe try new P2P object for each node

node = P2P(debug=True)
node.sender(8333, 5)
while True:
    cli, addr = node.accept()
    node.send('data', addr)
    node.disconnect(addr)
    break

print("SENDER DONE: 354")
val = node.receiver("192.168.0.24", 8339)
print(val)

""" terminate port in linux
kill -9 $(lsof -t -i:8333 -sTCP:LISTEN)
"""
