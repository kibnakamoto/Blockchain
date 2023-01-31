# transaction code for adding to mempool and data to send into the blocks
# includes a list of transactions resetted every block
from ecc import sha512, ecc, curves
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

# signature error, raised when the signature is not verified
class SignatureError(ValueError):
    pass

# transaction data format to sign
def tx_sign_data(prev_tx:str, block_index:int, b64_pub:bytes, amount: int, b64_pri:bytes):
    return sha512.Sha512(sha512.Sha512(int.to_bytes(constants.VERSION, 4, 'big') + prev_tx.encode('utf-8') +
                                       str(block_index).encode('utf-8') + b64_pub + b64_pri +
                                       str(amount).encode('utf-8')).digest()).digest().decode('charmap') # message to sign

# transaction structure, used by the person who is sending
class TxStructure:
    """ Default Class Initializer """
    def __init__(self, pubk:tuple, amount:float, block_index:int, ecdsa: ecc.Ecdsa, wlt: wallet.Wallet):
        self.now = str(datetime.datetime.now())
        self.now = self.now.replace(' ', '-')
        self.amount = amount
        self.pubk = pubk # receiver
        self.block_index = block_index
        with open('user/rtransactions.json','r') as file:
            data = json.load(file)
            if data["transactions"] != []:
                tx_count = len(data["transactions"])
                self.prev_tx = data["transactions"][-1][str(tx_count-1)][-1]["hash"] # get previous transaction from user previous transactions
                self.prev_block_i = data["transactions"][-1][str(tx_count-1)][-1]["block index"]
                self.prev_amount = data["transactions"][-1][str(tx_count-1)][-1]["amount"]
                if self.prev_amount <= amount: # if previous transaction amount is smaller than requested amount
                    raise AmountError(f"Previous transactions don't supplement amount requested:\n\tamount requested: {self.amount}\n\tprevious transaction amount: {self.prev_amount}")
            else:
                self.prev_tx = "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
                self.prev_block_i = "0"

        # encode public key as base 64
        self.b64_pub = wallet.b64(wlt.pubkey)

        # encode private key as base 64
        self.b64_pri = base64.b64encode(str(wlt.prikey).encode('utf-8'))
        
        self.to_sign = tx_sign_data(self.prev_tx, self.block_index, self.b64_pub, self.amount, self.b64_pri) # message to sign
        self.signature = ecdsa.gen_signature(self.to_sign, wlt.prikey)
        self.m_hash = ecdsa.m_hash
        self.b64_signature = wallet.b64(self.signature)

        self.info = int.to_bytes(constants.VERSION, 4, 'big') + b" " + self.prev_tx.encode('utf-8') + b" " + self.b64_signature + b" " + \
                    str(self.block_index).encode('utf-8') + b" " + str(self.amount).encode('utf-8') + b" " + self.b64_pub
        self.b64_pub = self.b64_pub.decode('utf-8')
        self.b64_signature = self.b64_signature.decode('utf-8')
        self.tx_hash = sha512.Sha512(self.info).hexdigest()

# wallet is senders wallet
# pubk is receiver's wallet address
# amount of amount to send
class Transaction(TxStructure):
    def __init__(self, wlt: wallet.Wallet, pubk: tuple, amount: float, block_index:int): # checksum is the first 4 bytes of the wallet
        if amount <= 0.0:
            raise AmountError("negative or non-existent amount")
        self.ecdsa = ecc.Ecdsa()
        self.ecies = ecc.Ecies()
        super().__init__(pubk, amount, block_index, self.ecdsa, wlt)
        self.wallet = wlt
        self.fees = constants.calculate_fees(self.amount)

    # add transaction to mempool, check if amount <= balance, update balance, sign transaction with private key
    # transactions in mempool will be mined in mine.py then emptied. 
    # call after ownership verified
    def add_transaction(self):
        if self.amount+self.fees <= self.wallet.balance:
            mempool = open("mempool", "a") # transaction hash + timestamp + block_index + prev transaction + previous block index + amount
            mempool.write(self.tx_hash + " " + self.now + " " + str(self.block_index) + " " + self.prev_tx + " " + str(self.prev_block_i) + " " + self.b64_pub + " " +  self.b64_signature + " " + str(self.m_hash) + " " + str(self.amount) + "\n")
            mempool.close()
            self.wallet.balance-=self.amount
            self.wallet.balance-=self.fees
        else:
            raise AmountError(f"insufficient balance: {self.wallet.balance} left in balance while transaction requires {self.amount+self.fees} including fees")

    # saves transaction in user/prev_transactions.json
    def save(self):
        with open('user/prev_transactions.json','r+') as file:
            data = json.load(file)
            id = len(data["transactions"])-1 # id is the final values id, for order
            data_add = {
                "hash": self.tx_hash,
                "time": self.now,
                "private key": hex(self.wallet.prikey)[2:].zfill(8),
                "version": hex(constants.VERSION)[2:],
                "prev transaction": self.prev_tx,
                "signature": self.b64_signature,
                "to sign": self.to_sign,
                "block index": hex(self.block_index)[2:],
                "public key": self.b64_pub,
                "amount": self.amount
            }
            # This condition will only check if transaction is isn't saved in the id-1.
            # This will prevent save being called twice without another transaction in between.
            if id > 1:
                # TODO this if statement will not be secure against hash that isn't the final value.
                #      if id isn't len-1, it will pass through
                if self.tx_hash not in data["transactions"][-1][str(id)][0]["hash"]: # add if tx_hash isn't already saved
                    data["transactions"].append({str(id+1): [data_add]})
                    file.seek(0)
                    json.dump(data, file, indent=4)
            else: # if rtransactions is empty
                data["transactions"].append({id+1: [data_add]})
                file.seek(0)
                json.dump(data, file, indent=4)

# transaction receiver
# receives the sent signature and verifies transaction
# <params>
# wlt: wallet
# pubk: senders public key
# amount: amount of Kibcoin
# block_index: the index of the current block that will have this transaction
# tx_hash: transaction hash
# return: hexdigest of new transaction hash
def tx_receiver(wlt: wallet.Wallet, pubk: tuple, amount: float, block_index:int, tx_hash:str) -> str:
    ecdsa = ecc.Ecdsa()
    # verified = ecdsa.verify_signature(signature, int.from_bytes(data), pubk)
#    if verified:
    wlt.balance += amount
    b64_prikey = base64.b64encode(str(wlt.prikey).encode('utf-8'))
    sign_data = tx_sign_data(tx_hash, block_index, wallet.b64(wlt.pubkey), amount, b64_prikey)
    signature = ecdsa.gen_signature(sign_data, wlt.prikey) # generate new signature for new ownership
    with open('user/rtransactions.json','r+') as file:
        data = json.load(file)
        b64_signature = b""
        b64_signature += base64.b64encode(str(signature[0]).encode('utf-8'))
        b64_signature += b"|"
        b64_signature += base64.b64encode(str(signature[1]).encode('utf-8'))
        b64_pubk = b""
        b64_pubk += base64.b64encode(str(pubk[0]).encode('utf-8'))
        b64_pubk += b"|"
        b64_pubk += base64.b64encode(str(pubk[1]).encode('utf-8')) # senders public key
        new_hash_info = int.to_bytes(constants.VERSION, 4, 'big') + b" " + tx_hash.encode('utf-8') + b" " + b64_signature + b" " + \
                        str(block_index).encode('utf-8') + b" " + str(amount).encode('utf-8') + b" " + b64_pubk
        new_hash = sha512.Sha512(new_hash_info).hexdigest()
        data_add = { # new transaction
            "hash": new_hash,
            "time": str(datetime.datetime.now()),
            "private key": b64_prikey.decode('utf-8'),
            "version": hex(constants.VERSION)[2:],
            "prev transaction": tx_hash, # basically proof of income
            "signature": b64_signature.decode('utf-8'),
            "to sign": sign_data,
            "block index": hex(block_index)[2:],
            "public key": b64_pubk.decode('utf-8'),
            "amount": amount
        }
        id = len(data["transactions"])-1 # id of transaction (for ordering rtransactions.json)
        if id > 1:
            # TODO this if statement will not be secure against hash that isn't the final value.
            #      if id isn't len-1, it will pass through
            if tx_hash not in data["transactions"][-1][str(id)][0]["hash"]: # add if tx_hash isn't already saved
                data["transactions"].append({str(id+1): [data_add]})
                file.seek(0)
                json.dump(data, file, indent=4)
        else:
            data["transactions"].append({id+1: [data_add]})
            file.seek(0)
            json.dump(data, file, indent=4)
        return new_hash
#    else:
#        raise SignatureError("The signature isn\'t verified, false transaction, aborted")

# If the amount you want to send is bigger than the previous transaction, recursively call tx_receiver for your own
# transactions and combine their amounts. This way, your not creating money out of thin air and will be verified when mined.
# If you don't use this method, it will not successfully mine and the amount will be locked
# Basically sending money to yourself
# Maybe in future versions, try implementing multiple previous hashes

# In mining, verify if mempool transaction previous transaction exists in the specified block

""" for testing wallet verification and transaction making """
# alice and bob share their public keys and come up with their shared-secret
w = curves.Weierstrass(constants.CURVE.p, constants.CURVE.a, constants.CURVE.b)
alice = curves.Curve(constants.CURVE)
bob = curves.Curve(constants.CURVE)
alice.get_prikey()
bob.get_prikey()
alice.get_pubkey()
bob.get_pubkey()
a_shared_sec = w.multiply(bob.pub_k,alice.pri_k)[0]
b_shared_sec = w.multiply(alice.pub_k,bob.pri_k)[0]
a_shared_sec = ecc.hkdf(a_shared_sec)
b_shared_sec = ecc.hkdf(b_shared_sec)


# Alice
wlt = wallet.Wallet()
wlt.new_keys()
wlt_send = wlt.secure_com_sender(a_shared_sec)
checksum = wlt_send[0] # base64
ciphertext = wlt_send[1]

# send ciphertext ubytessing P2P node

# Bob
wlt1 = wallet.Wallet()
wlt1.new_keys()

# verify checksum to make sure connection is secure
verified_wallet_connection = wlt1.secure_com_receiver(b_shared_sec, ciphertext.decode('utf-8'), checksum)
if verified_wallet_connection:
    # continue with transaction
    # Bob sends transaction to Alice
    wlt1.balance = 50
    transaction = Transaction(wlt1, wlt.pubkey, 1.0, 0)
    transaction.add_transaction()
    transaction.save()

    # alice receives transaction
    print(tx_receiver(wlt, wlt1.pubkey, 5.0, 0, transaction.tx_hash))
    print("checksum: ", checksum)