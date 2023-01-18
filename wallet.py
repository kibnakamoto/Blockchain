# the wallet structure and account of buyers

import secrets
from ecc import sha512, curves
import constants
import hashlib
import base64

# make fingerprint into HMAC, message will be random
def gen_fingerprint(pubkey_x: int) -> bytes:
    base64.b
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

# geenrate message for encrypting for secure communication
# which is sending the public key and using hmac to verify that the message isn't verified
def gen_message():
    return secrets.token_bytes(16)

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
        self.weierstrass = curves.Weierstrass(curve.p, curve.a, curve.b)

    # create shared secret with receiver, create sender's shared_secret, the same thing will happen on receiver's side
    def secure_com_sender(self, receiver_pubk) -> str:
        shared_secret = self.weierstrass.multiply(receiver_pubk, self.prikey)[0]
        hkdf = ecc.hkdf(shared_secret) # aes256 key
        self.ecies = ecc.Ecies()
        msg = gen_message()
        self.fingerprint = self.ecies.hmac(msg, hkdf)[4:]
        ct = self.ecies.encrypt(msg, hkdf, None, None)
        return self.fingerprint + ct
        
    def secure_com_receiver(self, sender_pubk, ciphertext, fingerprint) -> bool:
        shared_secret = self.weierstrass.multiply(sender_pubk, self.prikey)[0]
        hkdf = ecc.hkdf(shared_secret) # aes256 key
        self.ecies = ecc.Ecies()
        pt = self.ecies.decrypt(ciphertext, hkdf, None, None)
        self.fingerprint = self.ecies.hmac(pt, hkdf)[:4]
        return self.fingerprint == fingerprint

        
        

    # create wallet address
    def create_wallet_address(self):
        if self.pubkey == None:
            self.new_keys()

        # calculate fingerprint
        # pubkey[0] is the compressed public key
        keccak256 = hashlib.sha3_256()
        keccak256.update(base64.b64encode(str(self.pubkey[0]).encode('utf-8')))
        fingerprint = sha512.Sha512(keccak256.digest()).digest()
    
        # add fingerprint with checksum (4 bytes of fingerprint hashed twice with keccak256)
        self.wallet_address = base64.b64encode(str(self.pubkey).encode('utf-8')).decode('utf-8')
        self.wallet_address = self.wallet_address.replace('=', '')
        self.wallet_address = fingerprint + self.wallet_address


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

# send to receiver


print(wallet.wallet_address)
