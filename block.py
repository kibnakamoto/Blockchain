# file for blocks structures and to be added into the blocks folder which is the blockchain

import secrets
import constants
import datetime
from .ecc import sha512

def gen_nonce() -> int:
    return secrets.randbelow(constants._2R64) # generate 64-bit nonce



class BlockHeader:
    def __init__(self, merkle_root:str, nonce:int, block_index:int, prev_hash:str, difficulty: int):
        self.merkle_root = merkle_root
        self.nonce = nonce
        self.block_index = block_index
        self.prev_hash = prev_hash # previous block header hash
        self.timestamp = str(datetime.datetime.now())
        self.version = int.to_bytes(constants.VERSION, 4, 'big')
        self.info = self.version + self.prev_hash.encode('utf-8') + self.merkle_root + self.timestamp.encode('utf-8') + \
                    int.to_bytes(difficulty, 4, 'big') + int.to_bytes(self.nonce, 8, 'big')
        self.block_hash = sha512.Sha512(self.info).hexdigest()


class Block(BlockHeader):
    def __init__(self):
        pass
