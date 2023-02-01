"""
 * Blockchain
 * Author: Taha Canturk
 * Author: Taha Canturk
 *  Github: kibnakamoto
 *  Project: Blockchain
 *    Date: Jan 31 - 2023
 *     Software Version: 1.0
"""

# Wallet file

import secrets
from ecc import ecc, sha512, curves
import constants
import base64

# fingerprint of receiver
def gen_fingerprint_r(hkdf: int, ciphertext) -> bytes:
    ecies = ecc.Ecies()
    pt = ecies.decrypt(ciphertext, hkdf, None, None)
    fingerprint = ecies.gen_hmac(pt, hkdf)[:4].encode('utf-8')
    return fingerprint

# fingerprint of sender
def gen_fingerprint_s(hkdf: int, plaintext:str) -> tuple:
    ecies = ecc.Ecies()
    fingerprint = ecies.gen_hmac(plaintext, hkdf)[:4].encode('utf-8')
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
def gen_message() -> str:
    string = ""
    for i in range(16):
        string += chr(secrets.randbelow(128))
    return string

# tuple to base64 bytes
def b64(data:tuple) -> bytes:
    new_data = b""
    for i in range(len(data)):
        new_data += base64.b64encode(str(data[i]).encode('utf-8'))

        # add delimeter so the x,y coordinates are known
        if i < len(data)-1:
            new_data += b"|"

    return new_data

# base64 to tuple
def b64_d(data:str) -> tuple[int, int]:
    data_list = data.split('|')
    return (int(base64.b64decode(data_list[0]).decode('utf-8')), int(base64.b64decode(data_list[1]).decode('utf-8')))

# Cryptocurrency wallet
class Wallet:
    def __init__(self):
        self.pubkey = None # Public Key also public wallet address
        self.prikey = None # Corrosponding Private Key
        self.balance = 0 # account balance
        self.wallet_address = None # base64 pubkey

    def new_keys(self):
        curve = curves.Curve(constants.CURVE)
        curve.get_prikey()
        curve.get_pubkey()
        self.pubkey = curve.pub_k
        self.prikey = curve.pri_k
        self.wallet_address = b64(self.pubkey)
        self.weierstrass = curves.Weierstrass(constants.CURVE.p, constants.CURVE.a, constants.CURVE.b)

    # creates a secure communication from senders side. the same thing will happen on receiver's side
    # generates checksum
    def secure_com_sender(self, shared_secret) -> tuple:
        self.msg = gen_message()
        self.fingerprint = gen_fingerprint_s(shared_secret, self.msg)
        return base64.b64encode(gen_checksum(self.fingerprint[0])), self.fingerprint[1] # 1 is for ciphertext
        
    # secure communication from receiver's side. Checks checksum
    def secure_com_receiver(self, shared_secret:int, ciphertext:str, checksum:bytes) -> bool:
        # shared_secret is equal to hkdf key
        self.fingerprint = gen_fingerprint_r(shared_secret, ciphertext)[:4]
        return base64.b64encode(gen_checksum(self.fingerprint)) == checksum
