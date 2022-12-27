# This file is for the peer-to-peer network for nodes to communicate with each other
from p2pnetwork.node import Node
from pyp2p.net import *
import requests
import time

# node_callback
#  event         : event name
#  node          : the node (Node) that holds the node connections
#  connected_node: the node (NodeConnection) that is involved
#  data          : data that is send by the node (could be empty)
def node_callback(event, node, connected_node, data):
    try:
        if event != 'node_request_to_stop': # node_request_to_stop does not have any connected_node, while it is the main_node that is stopping!
            print('Event: {} from main node {}: connected node {}: {}'.format(event, node.id, connected_node.id, data))

    except Exception as e:
        print(e)
# 192.168.0.24
# Peer to Peer network without tor
class P2P_No_TOR:
    def __init__(self, debug=False):
        self.node = Node('127.0.0.1', 10001, node_callback)
        self.node.debug = debug
        self.id = self.node.id


    def start(self):
        self.node.start()
        time.sleep(5)

    def stop(self):
        self.node.stop()

x = P2P_No_TOR(True)
x.start()

stupid_node = Node('192.168.0.19', 10002)
stupid_node.start()
# Connect to another node, otherwise you do not have any network

# x.node.init_server()
# x.node.sock.listen(50)
x.node.connect_with_node('192.168.0.19', 10002)
x.node.send_to_nodes('{"message": "hoi from node 1"}')
time.sleep(50)
# Send some message to the other nodes

x.stop()
