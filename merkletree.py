"""
 * Blockchain
 * Author: Taha Canturk
 * Author: Taha Canturk
 *  Github: kibnakamoto
 *  Project: Blockchain
 *    Date: Jan 31 - 2023
 *     Software Version: 1.0
"""
from ecc.ecc import Ecdsa
from ecc.sha512 import Sha512
from wallet import b64_d

# get transaction hashes and public keys from mempool
def get_mempool_verification_data() -> tuple[list[str], list[tuple[int, int]], list[tuple[int, int]], list[int], list[bool]]:
    hashes = []
    pubks = []
    signatures = []
    m_hashes = []
    verified = []
    ecdsa = Ecdsa()
    with open("mempool", 'r') as mempool:
        lines = mempool.readlines()
        for line in lines:
            line = line.split(' ')
            hashes.append(line[0])
            pubks.append(b64_d(line[5]))
            signatures.append(b64_d(line[6]))
            m_hashes.append(int(line[7]))
            verified.append(ecdsa.verify_signature(signatures[-1], m_hashes[-1],  pubks[-1]))
    return hashes, pubks, signatures, m_hashes, verified

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

        # if amount of transactions isn't able to make a merkle-tree
        if len(self.transactions)%2 != 0:
            self.transactions.append('0'*64)
            

    def get_root(self) -> str:
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
