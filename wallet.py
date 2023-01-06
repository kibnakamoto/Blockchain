# the wallet structure and account of buyers

import secrets
from ecc import sha512, curves
import constants
import hashlib
import base64

def gen_fingerprint(pubkey_x: int) -> bytes:
    keccak256 = hashlib.sha3_256()
    keccak256.update(base64.b64encode(str(pubkey_x).encode('utf-8')))
    return sha512.Sha512(keccak256.digest()).digest()
    
# fingerprint is encoded fingerprint
def gen_checksum(fingerprint: bytes) -> bytes:
    keccak256 = hashlib.sha3_256()
    keccak256.update(fingerprint)
    return keccak256.digest()[:4]

# this process is to be done by the receiver. if Bob sends wallet address to Alice, Alice then
# needs to generate the checksum using the fingerprint(hash of public key) and check the bob's checksum
def verify_checksum(fingerprint, checksum): # 4 byte checksum
    return gen_checksum(fingerprint) == checksum

# Cryptocurrency wallet
class Wallet:
    def __init__(self):
        self.wallet_address = None # wallet address that is the key for the wallet
        self.pubkey = None # Public Key
        self.prikey = None # Corrosponding Private Key
        self.balance = 0 # account balance
    
    def new_keys(self):
        curve = curves.Curve(constants.CURVE())
        curve.get_prikey()
        curve.get_pubkey()
        self.pubkey = curve.pub_k
        self.prikey = curve.pri_k
    
    # create wallet address
    def create_wallet_address(self):
        if self.pubkey == None:
            self.new_keys()

        # pubkey[0] is the compressed public key
        keccak256 = hashlib.sha3_256()
        keccak256.update(base64.b64encode(str(self.pubkey[0]).encode('utf-8')))
        fingerprint = sha512.Sha512(keccak256.digest()).digest()

        # calculate wallet address where fingerprint is bytes
        # add fingerprint with checksum (4 bytes of fingerprint hashed twice with keccak256)
        keccak256 = hashlib.sha3_256()
        keccak256.update(fingerprint)
        keccak256.update(keccak256.digest())
        self.wallet_address = base64.b64encode(fingerprint + keccak256.digest()[:4]).decode('utf-8')
        self.wallet_address = self.wallet_address.replace('=', '')


    def hex(self):
        padding = ((3-(len(self.wallet_address))) % 3) # pad because every = sign was replaced
        return base64.b64decode(self.wallet_address.encode('utf-8')+b'='*padding).hex()

    def int(self):
        try:
            return int(self.wallet_address,16)
        except ValueError:
            return int(self.hex(),16)

    # length in base64 without padding
    def __len__(self):
        return len(str(self.wallet_address))

wallet = Wallet()
wallet.new_keys()
wallet.create_wallet_address()
print(wallet.wallet_address)
