# transaction code for adding to mempool and data to send into the blocks
# includes a list of transactions resetted every block

from ecc import sha512, ecc
import wallet
import constants
import datetime
import os
import base64
import json
# import subprocess

# amount error, raised when the amount to transact is bigger than balance in wallet.
class AmountError(ValueError):
    pass

# transaction data format to sign
def tx_sign_data(prev_tx:str, block_index:int, b64_pub:bytes, amount: int):
    return sha512.Sha512(str(constants.VERSION).decode('hex') + prev_tx.encode('utf-8') + \
           hex(block_index)[2:].decode('hex') + b64_pub + hex(amount)[2:].decode('hex')).digest() # message to sign

# transaction structure, used by the person who is sending
class TxStructure:
    """ Default Class Initializer """
    def __init__(self, pubk:tuple, amount:float, block_index:int, ecdsa: ecc.Ecdsa, wlt: wallet.Wallet):
        self.now = datetime.datetime.now()
        self.amount = amount
        self.pubk = pubk # receiver
        self.block_index = block_index
        if not os.stat("user/prev_transactions.json").st_size != 0:
            with open('user/prev_transactions.json','r') as file:
                data = json.load(file)
                self.prev_tx = data["transactions"][len(data)-1].keys()[0] # get previous transaction from user previous transactions
            # self.prev_tx = subprocess.check_output(['tail', '-1', 'prev_mempool']).remove('\n') # get previous transaction from mempool previous transactions
        else:
            self.prev_tx = "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

        # encode public key as base 64
        self.b64_pub = b""
        self.b64_pub += base64.b64encode(hex(self.pubk[0])[2:].decode('hex'))
        self.b64_pub += b"|"
        self.b64_pub += base64.b64encode(hex(self.pubk[1])[2:].decode('hex'))

        self.to_sign = tx_sign_data(self.prev_tx, self.block_index, self.b64_pub, self.amount) # message to sign
        self.signature = ecdsa.gen_signature(self.to_sign, wlt.prikey)
        self.m_hash = ecdsa.m_hash
        self.b64_signature = b""
        self.b64_signature += base64.b64encode(hex(self.signature[0])[2:].decode('hex'))
        self.b64_signature += b"|"
        self.b64_signature += base64.b64encode(hex(self.signature[1])[2:].decode('hex'))

        self.info = str(constants.VERSION).decode('hex') + self.prev_tx.encode('utf-8') + self.b64_signature + \
                    hex(self.block_index)[2:].decode('hex') + hex(self.amount)[2:].decode('hex') + self.b64_pub
        self.tx_hash = sha512.Sha512(self.info).hexdigest()

# wallet is senders wallet
# wallet address is receiver's wallet address
# amount of amount to send
class Transaction(TxStructure):
    def __init__(self, wlt: wallet.Wallet, pubk: tuple, amount: float, block_index:int): # checksum is the first 4 bytes of the wallet
        self.ecdsa = ecc.Ecdsa()
        self.ecies = ecc.Ecies()
        super().__init__(pubk, amount, block_index, self.ecdsa, wlt)
        self.wallet = wlt
        self.amount = amount
        self.fees = constants.calculate_fees(self.amount)

    # add transaction to mempool, check if amount <= balance, update balance, sign transaction with private key
    # transactions in mempool will be mined in mine.py then emptied. 
    # call after ownership verified
    def add_transaction(self):
        if self.amount+self.fees <= self.wallet.balance:
            mempool = open("mempool", "w")  # write mode
            mempool.write(self.tx_hash + self.now + "\n")
            mempool.close()
            self.wallet.balance-=self.amount
            self.wallet.balance-=self.fees
        else:
            raise AmountError(f"insufficient balance: {self.wallet.balance} left in balance while transaction requires {self.amount+self.fees} including fees")

    # saves transaction in user/prev_transactions.json
    def save(self):
        with open('user/prev_transactions.json','r+') as file:
            data = json.load(file)
            id = len(data)-1 # id is the final values id, for order
            data_add = {
                "time": self.now,
                "private key": hex(self.wallet.prikey)[2:],
                "version": hex(constants.VERSION)[2:],
                "prev transaction": self.prev_tx,
                "signature": self.b64_signature,
                "to_sign": self.to_sign,
                "block_index": hex(self.block_index)[2:],
                "public key": self.b64_pub,
            }
            # This condition will only check if transaction is isn't saved in the id-1.
            # This will prevent save being called twice without another transaction in between.
            if self.tx_hash not in data["transactions"][id-1]: # add if tx_hash isn't already saved
                data["transactions"].append({id: {self.tx_hash: [data_add]}})
                file.seek(0)
                json.dump(data, file, indent=4)
