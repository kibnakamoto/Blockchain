# contant numbers that may be required in other files.

# from ecc.curves import Secp521r1
from ecc.curves import Secp521r1
from ecc.sha512 import Sha512
from ecc.aes import Aes256
import base64
from hashlib import sha256

# blockchain version
global VERSION

# 2 raied to x
global _2R16
global _2R32 
global _2R64 
global _2R128
global _2R256
global _2R512

global TOTAL_COINS # total amount of coins

# Cryptography Constants for Blockchain
global CURVE
global CURVE_SIZE
global SHA256_HASHLEN
global SHA512_HASHLEN
global SHA256_BLOCK_SIZE
global SHA512_BLOCK_SIZE
global HKDF_SIZE
global HKDF_HASHF
global SYMM_ALG # symmetric encryption algorithm

VERSION = 0x00000001

_2R16 = 0x10000
_2R32 = 0x100000000
_2R64 = 0x10000000000000000
_2R128 = 0x100000000000000000000000000000000
_2R256 = 0x10000000000000000000000000000000000000000000000000000000000000000
_2R512 = 0x100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

# market cap limit
TOTAL_COINS = 10000000

# elliptic curve
CURVE = Secp521r1() # P-521
CURVE_SIZE = 66 # length of shared key in octets 
SHA256_HASHLEN = 32 # length of hash output in octets                              
SHA512_HASHLEN = 64 # length of hash output in octets                              
SHA256_BLOCK_SIZE = 64 # length of single block in octets in hashing algorithm
SHA512_BLOCK_SIZE = 128
HKDF_SIZE = 32 # length of HKDF output in octects                           
HKDF_HASHF = sha256 # hashing algorithm used in HKDF                        
SYMM_ALG = Aes256 # ECIES Symmetric Encryption Algorithm          

# use sha256 for hkdf, and sha512 for hmac

# default encoding is base 64

# miners fee of a transaction
def calculate_fees(amount: float) -> float:
    return (amount/100)*1.00001 # fixed fee of 0.01%