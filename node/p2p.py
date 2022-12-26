# This file is for the peer-to-peer network for nodes to communicate with each other
from p2pnetwork.node import Node
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

# Peer to Peer network without tor
class P2P_No_TOR:
    def __init__(self):
        self.ip = requests.get("https://ident.me").text # get ip of node
        self.node = Node('127.0.0.1', 10001, node_callback)

    def start(self):
        self.node.start()
        time.sleep(1)

    def stop(self):
        self.node.stop()

x = P2P_No_TOR()
x.start()

# Connect to another node, otherwise you do not have any network.
x.node.connect_with_node('127.0.0.1', 10002)
time.sleep(2)
# Send some message to the other nodes
x.node.send_to_nodes('{"message": "hoi from node 1"}')

x.stop()
