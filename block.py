# file for blocks structures and to be added into the blocks folder which is the blockchain
import constants
from ecc import sha512

import secrets
import datetime
import struct
import os
import json

def gen_nonce() -> int:
    return secrets.randbelow(constants._2R64) # generate 64-bit nonce

# generate target for sha512 using bits
def gen_target(bits) -> int:
    exp = bits >> 48
    mant = bits & 0xffffffffffff
    target = '%064x' % (mant * (1<<(16*(exp - 3))))
    target = int(target,16)
    return target

# TODO: define bits for target
def gen_bits():
    pass

class BlockHeader:
    def __init__(self, merkle_root:str, nonce:int, block_index:int, prev_hash:str, difficulty: float, bits):
        self.merkle_root = merkle_root
        self.nonce = nonce
        self.block_index = block_index
        self.prev_hash = prev_hash # previous block header hash
        self.timestamp = str(datetime.datetime.now())
        self.version = int.to_bytes(constants.VERSION, 4, 'big')
        self.bits = bits # 8 bytes
        self.info = self.version + self.prev_hash.encode('utf-8') + self.merkle_root + self.timestamp.encode('utf-8') + \
                    bytearray(struct.pack("f", difficulty)) + int.to_bytes(self.nonce, 8, 'big')
        self.block_hash = sha512.Sha512(self.info).hexdigest()
        self.json = {
            "hash": self.block_hash,
            "prev hash": self.prev_hash,
            "bits": self.bits,
            "timestamp": self.timestamp,
            "merkle root": self.merkle_root,
            "nonce": self.nonce
        }

    # add block to blocks folder
    # transactions: transactions used to calculate merkle root, the direct line from mempool. NOT JUST HASH
    def add_block(self, transactions) -> None:
        os.makedirs("user/{self.block_index}")
        
        # append self.json to block
        with open(f"user/{self.block_index}/block.json", 'w') as file:
            data = json.dumps(self.json, indent=4)
            file.write(data)

        # append all transactions included in Merkle Tree in transactions
        with open(f"user/{self.block_index}/transactions", 'w') as file:
            for transaction in transactions:
                file.write(transaction + "\n")

class Block(BlockHeader):
    def __init__(self):
        pass
