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
    return sha512.Sha512(sha512.Sha512(str(constants.VERSION).decode('hex') + prev_tx.encode('utf-8') +
                                       int.to_bytes(block_index) + b64_pub + b64_pri +
                                       int.to_bytes(amount)).digest()).digest() # message to sign

# transaction structure, used by the person who is sending
class TxStructure:
    """ Default Class Initializer """
    def __init__(self, pubk:tuple, amount:float, block_index:int, ecdsa: ecc.Ecdsa, wlt: wallet.Wallet):
        self.now = datetime.datetime.now()
        self.amount = amount
        self.pubk = pubk # receiver
        self.block_index = block_index
        if not os.stat("user/rtransactions.json").st_size != 0:
            with open('user/rtransactions.json','r') as file:
                data = json.load(file)
                self.prev_tx = data["transactions"][len(data)-1].keys()[0] # get previous transaction from user previous transactions
            # self.prev_tx = subprocess.check_output(['tail', '-1', 'prev_mempool']).remove('\n') # get previous transaction from mempool previous transactions
        else:
            self.prev_tx = "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

        # encode public key as base 64
        self.b64_pub = b""
        self.b64_pub += base64.b64encode(int.to_bytes(self.pubk[0]))
        self.b64_pub += b"|"
        self.b64_pub += base64.b64encode(int.to_bytes(self.pubk[1]))

        # encode private key as base 64
        self.b64_pri = base64.b64encode(int.to_bytes(wlt.prikey))
        
        self.to_sign = tx_sign_data(self.prev_tx, self.block_index, self.b64_pub, self.amount, self.b64_pri) # message to sign
        self.signature = ecdsa.gen_signature(self.to_sign, wlt.prikey)
        self.m_hash = ecdsa.m_hash
        self.b64_signature = b""
        self.b64_signature += base64.b64encode(int.to_bytes(self.signature[0]))
        self.b64_signature += b"|"
        self.b64_signature += base64.b64encode(int.to_bytes(self.signature[1]))

        self.info = str(constants.VERSION).decode('hex') + b" " + self.prev_tx.encode('utf-8') + b" " + self.b64_signature + b" " + \
                    int.to_bytes(self.block_index) + b" " + int.to_bytes(self.amount) + b" " + self.b64_pub
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
        self.fees = constants.calculate_fees(self.amount)

    # add transaction to mempool, check if amount <= balance, update balance, sign transaction with private key
    # transactions in mempool will be mined in mine.py then emptied. 
    # call after ownership verified
    def add_transaction(self):
        if self.amount+self.fees <= self.wallet.balance:
            mempool = open("mempool", "w")
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
                "to sign": self.to_sign,
                "block index": hex(self.block_index)[2:],
                "public key": self.b64_pub,
            }
            # This condition will only check if transaction is isn't saved in the id-1.
            # This will prevent save being called twice without another transaction in between.
            if id >= -1:
                if self.tx_hash not in data["transactions"][id-1]: # add if tx_hash isn't already saved
                    data["transactions"].append({id: {self.tx_hash: [data_add]}})
                    file.seek(0)
                    json.dump(data, file, indent=4)
            else: # if rtransactions is empty
                data["transactions"].append({id: {self.tx_hash: [data_add]}})
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
    # TODO: to verify that the signature isn't made up. let sender share block index and timing and transaction hash of the sent hash to everyone so that
    #       nodes can find check if transaction exists in the given block
    ecdsa = ecc.Ecdsa()
    # verified = ecdsa.verify_signature(signature, int.from_bytes(data), pubk)
#    if verified:
    wlt.balance += amount
    b64_prikey = base64.b64encode(int.to_bytes(wlt.prikey))
    sign_data = tx_sign_data(tx_hash, block_index, wlt.b64(wlt.pubkey), amount, b64_prikey)
    signature = ecdsa.gen_signature(sign_data, wlt.prikey) # genereate new signature for new ownership
    with open('user/rtransactions.json','w') as file:
        data = json.load(file)
        b64_signature = b""
        b64_signature += base64.b64encode(int.to_bytes(signature[0]))
        b64_signature += b"|"
        b64_signature += base64.b64encode(int.to_bytes(signature[1]))
        b64_pubk = b""
        b64_pubk += base64.b64encode(int.to_bytes(pubk[0]))
        b64_pubk += b"|"
        b64_pubk += base64.b64encode(int.to_bytes(pubk[1])) # senders public key
        new_hash_info = str(constants.VERSION).decode('hex') + b" " + tx_hash.encode('utf-8') + b" " + b64_signature + b" " + \
                        int.to_bytes(block_index) + b" " + int.to_bytes(amount) + b" " + b64_pubk
        new_hash = sha512.Sha512(new_hash_info).hexdigest()
        data_add = { # new transaction
            "time": str(datetime.datetime.now()),
            "private key": b64_prikey,
            "version": hex(constants.VERSION)[2:],
            "prev transaction": tx_hash, # basically proof of income
            "signature": b64_signature,
            "to sign": sign_data,
            "block index": hex(block_index)[2:],
            "public key": b64_pubk,
        }
        id = len(data) # id of transaction (for ordering rtransactions.json)
        if id != 0:
            id-=1
            # This condition will only check if transaction is isn't saved in the id-1.
            # This will prevent save being called twice without another transaction in between.
            if new_hash not in data["transactions"][id-1]: # add if tx_hash isn't already saved
                data["transactions"].append({id: {new_hash: [data_add]}})
                file.seek(0)
                json.dump(data, file, indent=4)
        else:
            data["transactions"].append({0: {new_hash: [data_add]}})
            file.seek(0)
            json.dump(data, file, indent=4)
        return new_hash
#    else:
#        raise SignatureError("The signature isn\'t verified, false transaction, aborted")

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
print(verified_wallet_connection)
if verified_wallet_connection:
    # continue with transaction
    # Bob sends transaction to Alice
    wlt1.balance = 50
    transaction = Transaction(wlt1, bob.pub_k, 1.0, 0)