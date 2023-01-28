from ecc.sha512 import Sha512

class MerkleTreeNode:
    # default class contructor
    def __init__(self, data:str):
        self.left = None
        self.right = None
        self.data = data
        self.hash = Sha512(self.data.encode('utf-8')).hexdigest()


class MerkleTree:
    # default class constructor
    def __init__(self, transactions:list[str]):
        self.transactions = transactions

    def get_root(self):
        nodes = list()
        for transaction in self.transactions:
            nodes.append(MerkleTreeNode(transaction))

        while len(nodes) != 1:
            temp = list()
            for i in range(0, len(nodes), 2):
                node1 = nodes[i]
                if i+1 < len(nodes):
                    node2 = nodes[i+1]
                else:
                    temp.append(nodes[i])
                    break
                node = MerkleTreeNode(node1.hash + node2.hash)
                node.left = node1
                node.right = node2
                temp.append(node)
            nodes = temp
        return nodes[0].hash

# testing
hashes = list()
for i in range(4):
    hashes.append(Sha512(str(i).encode('utf-8')).hexdigest())

merkletree = MerkleTree(hashes)
print(merkletree.get_root())