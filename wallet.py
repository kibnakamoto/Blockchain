# the wallet structure and account of buyers

import secrets
from ecc import ecc, sha512, curves
import constants
import base64

# fingerprint of receiver
def gen_fingerprint_r(shared_secret: int, ciphertext) -> bytes:
    hkdf = ecc.hkdf(shared_secret) # aes256 key
    ecies = ecc.Ecies()
    pt = ecies.decrypt(ciphertext, hkdf, None, None)
    fingerprint = ecies.hmac(pt, hkdf)[:4]
    return fingerprint

# fingerprint of sender
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
        self.wallet_address = None # base64 pubkey

    def new_keys(self):
        curve = curves.Curve(constants.CURVE())
        curve.get_prikey()
        curve.get_pubkey()
        self.pubkey = curve.pub_k
        self.prikey = curve.pri_k
        self.wallet_address = self.b64(self.pubkey)
        self.weierstrass = curves.Weierstrass(curve.p, curve.a, curve.b)

    # create shared secret with receiver, create sender's shared_secret, the same thing will happen on receiver's side
    def secure_com_sender(self, shared_secret) -> bytes:
        self.fingerprint = gen_fingerprint_s(shared_secret, gen_message())
        return base64.b64encode(self.fingerprint[0] + self.fingerprint[1])
        
    def secure_com_receiver(self, shared_secret:int, ciphertext:str, fingerprint:bytes) -> bool:
        self.fingerprint = gen_fingerprint_r(shared_secret, ciphertext)[4:]
        return base64.b64encode(self.fingerprint) == fingerprint

    # tuple to base64 bytes
    def b64(self, data:tuple) -> bytes:
        new_data = b""
        for i in range(len(data)):
            new_data += base64.b64encode(hex(data[i])[2:].decode('hex'))

            # add delimeter so the x,y coordinates are known
            if i < len(data)-1:
                new_data += b"|"

        return new_data
    
    # base64 to tuple
    def b64_d(self, data:bytes):
        data_list = data.decode('utf-8').split('|')
        return (base64.b64decode(data_list[0]), base64.b64decode(data_list[1]))

wallet = Wallet()
wallet.new_keys()
wallet.create_pubkey()

print(wallet.pubkey)
