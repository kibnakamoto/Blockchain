# the wallet structure and account of buyers

import secrets
from ecc import ecc, sha512, curves
import constants
import hashlib
import base64

# fingerprint of receiver
def gen_fingerprint_r(shared_secret: int, ciphertext) -> bytes:
    hkdf = ecc.hkdf(shared_secret) # aes256 key
    ecies = ecc.Ecies()
    pt = ecies.decrypt(ciphertext, hkdf, None, None)
    fingerprint = ecies.hmac(pt, hkdf)[:4]
    return fingerprint

def gen_fingerprint_s(shared_secret: int, plaintext) -> tuple:
    hkdf = ecc.hkdf(shared_secret) # aes256 key
    ecies = ecc.Ecies()
    fingerprint = ecies.hmac(plaintext, hkdf)[:4]
    ct = ecies.encrypt(plaintext, hkdf, None, None)
    return fingerprint, ct.encode('utf-8')


# fingerprint is encoded fingerprint
def gen_checksum(fingerprint: bytes) -> bytes:
    checksum = sha512.Sha512(fingerprint).digest()[:4]
    return checksum

# this process is to be done by the receiver. if Bob sends wallet address to Alice, Alice then
# needs to generate the checksum using the fingerprint(hash of public key) and check the bob's checksum
def verify_checksum(fingerprint, checksum) -> bool: # 4 byte checksum
    return gen_checksum(fingerprint) == checksum

# geenrate message for encrypting for secure communication
# which is sending the public key and using hmac to verify that the message isn't verified
def gen_message() -> bytes:
    return secrets.token_bytes(16)

# Cryptocurrency wallet
class Wallet:
    def __init__(self):
        self.pubkey = None # Public Key also public wallet address
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
    def secure_com_sender(self, shared_secret) -> bytes:
        self.fingerprint = gen_fingerprint_s(shared_secret, gen_message())
        return self.fingerprint[0] + self.fingerprint[1]
        
    def secure_com_receiver(self, shared_secret, ciphertext, fingerprint) -> bool:
        self.fingerprint = gen_fingerprint_r(shared_secret, ciphertext)[4:]
        return self.fingerprint == fingerprint

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
