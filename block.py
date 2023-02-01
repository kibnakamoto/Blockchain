"""
 * Blockchain
 * Author: Taha Canturk
 * Author: Taha Canturk
 *  Github: kibnakamoto
 *  Project: Blockchain
 *    Date: Jan 31 - 2023
 *     Software Version: 1.0
"""

# file for blocks structures and to be added into the blocks folder which is the blockchain
import constants
import merkletree
from ecc import sha512

import secrets
import datetime
import os
import json

def gen_nonce() -> int:
    return secrets.randbelow(constants._2R64) # generate 64-bit nonce

# calculate target for sha512 using bits
def target_from_bits(bits:int) -> int:
    exp = bits >> 48
    mant = bits & 0xffffffffffff
    target = '%064x' % (mant * (1<<(16*(exp - 3))))
    target = int(target,16)
    return target

# calculate bits from target
# calculate target in base256
# if first value of base256 target is bigger than 0x7f, append 0 to the beggining
# add length of base256 target to the first 6 bytes of base256 target
def bits_from_target(target) -> int:
    base256 = bytearray(target.to_bytes((target.bit_length()+7)//8, 'big'))
    if base256[0] > 0x7f:
        base256 = int.to_bytes(0, 1, 'big') + base256
    base256 = int.to_bytes(len(base256), 3, 'big') + base256[:6]
    return int.from_bytes(base256, 'big')

# get difficulty in compact target bits
# uses same algorithm as Bitcoin
# https://bitcoin.stackexchange.com/questions/2924/how-to-calculate-new-bits-value
# basic pseudo-code: 
# new_target = last_block.nBits.uncompress();
# new_target *= actual_timespan;
# new_target /= target_timespan;
# this_block.nBits = new_target.compress();
def get_difficulty_target():
    block_count = os.listdir("blocks")
    if block_count%2016 == 0:
        block1 = json.load(open(f"blocks/{block_count-2}/block.json"))
        block2 = json.load(open(f"blocks/{block_count-1}/block.json"))
        format = "%d-%m-%y %H:%M:%S.%f" 
        date1 = datetime.datetime.strptime(block1["timestamp"], format)
        date2 = datetime.datetime.strptime(block2["timestamp"], format)
        difference = abs(date1-date2)
        if hasattr(difference, "month"):
            if difference.month > 2:
                constants.human_difficulty = 8
        elif hasattr(difference, "days"):
            if difference.day < 4:
                constants.human_difficulty = 0.5
        result = constants.target*difference.total_seconds()
        result/=1209600.0 # two weeks
        if result > constants._2R512: # if bigger than MAX_TARGET
            constants.target = constants._2R512
        else:
            constants.target = int(result)



class BlockHeader:
    def __init__(self, merkle_root:str, nonce:int, block_index:int, prev_hash:str, bits:int):
        self.merkle_root = merkle_root
        self.nonce = nonce
        self.block_index = block_index
        self.prev_hash = prev_hash # previous block header hash
        self.timestamp = str(datetime.datetime.now())
        self.version = int.to_bytes(constants.VERSION, 4, 'big')
        self.bits = bits # 8 bytes
        self.info = self.version.decode('utf-8') + self.prev_hash + self.merkle_root + self.timestamp + \
                    str(bits) + str(self.nonce)
        self.block_hash = sha512.Sha512(self.info).hexdigest()
        self.json = {
            "hash": self.block_hash,
            "prev hash": self.prev_hash,
            "bits": hex(self.bits)[2:],
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
        open("mempool", 'w') # delete contents of mempool

# find if a transaction exists
# tx_line: transaction line from unpack_mempool
def transaction_exists(tx_line:list[list[str]]) -> bool:
    # transaction hash + timestamp + block_index + prev transaction + previous block index + amount
    prev_tx = tx_line[3]
    prev_line = tx_line[4]
    try:
        with open(f"blocks/{prev_line}/transactions", "r") as f:
            data = f.readlines()
            for line in data:
                if line.split(' ')[0] == prev_tx:
                    return True
    except FileNotFoundError:
        return False

# get values from mempool
def unpack_mempool() -> list[list[str]]:
    with open("mempool", "r") as mempool:
        data = mempool.readlines()
        lst = []
        for line in data:
            lst.append(line.split(' '))
    return lst

class Block(BlockHeader):
    def __init__(self, nonce:int, transactions:list[str]):
        self.mempool = unpack_mempool()
        self.nonce = nonce
        self.transactions = transactions
        tx_line_i = 0
        while self.mempool and tx_line_i < len(self.mempool): # check if all transaction exists
            tx_line = self.mempool[tx_line_i]
            if not transaction_exists(tx_line):
                del self.mempool[tx_line_i]
            tx_line_i += 1
        blocks_len = len(os.listdir("blocks")) # block index

        if blocks_len != 0:
            # access previous block data
            with open(f"blocks/{blocks_len-1}/block.json") as f:
                data = json.load(f)
                prev_hash = data["hash"]
                del data
        else:
            prev_hash = "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        super().__init__(merkle_root=merkletree.MerkleTree(self.transactions).get_root(), nonce=self.nonce, block_index=blocks_len, prev_hash=prev_hash, bits=bits_from_target(constants.target))
