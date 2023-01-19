# transaction code for adding to mempool and data to send into the blocks
# includes a list of transactions resetted every block

from ecc import sha512, ecc, curves
import wallet
import constants
import datetime
import subprocess
import os

# encode integer
def encode_int(num, encoding='utf-8'):
    return str(num).encode(encoding)

# decode into integer
def decode_int(encoded, encoding='utf-8'):
    return int(encoded.decode(encoding))

version = verison of blockchain - 4 bytes in hex

prev_tx = previous verified transaction hash, from prev_mempool. get first value from prev_transaction then delete the prev_transaction from prev_mempool.

signature = proof of ownership, ECDSA signature, defined in *Section 1.1*

block_index = index of block

public_key = public key of receiver


# transaction structure
class TxStructure:
    def __init__(self, pubk:tuple, amount:float, block_index:int):
        now = datetime.datetime.now()
        self.amount = amount
        self.pubk = pubk
        if not os.stat("prev_mempool").st_size == 0:
            self.prev_tx = subprocess.check_output(['tail', '-1', 'prev_mempool']).remove('\n') # get previous transaction from mempool
        else:
            self.prev_tx = "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        
        self.block_index = block_index
        


# wallet is senders wallet
# wallet address is receiver's wallet address
# amount of amount to send
class Transaction(TxStructure):
    def __init__(self, wlt: wallet.Wallet, pubk: tuple, amount: float, block_index:int): # checksum is the first 4 bytes of the wallet
        super().__init__(pubk, amount, block_index)
        self.wallet = wlt
        self.ecdsa = ecc.Ecdsa()
        self.ecies = ecc.Ecies()

    def add_transaction(self):
        # TODO: add transaction to mempool, check if amount <= balance, update balance, sign transaction with private key
        #       transactions in mempool will be mined in mine.py then emptied. 
        pass

    def sign_transaction(self):
        pass

# send money in a transaction
class Send(Transaction):
    pass

# receive money in a transaction
class Receive(Transaction):
    pass