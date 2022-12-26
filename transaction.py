# transaction code for adding to mempool and data to send into the blocks
# includes a list of transactions resetted every block

from ecc, import sha512, ecc, curves
import wallet

# encode integer
def encode_int(num, encoding='utf-8'):
    return str(num).encode(encoding)

# decode into integer
def decode_int(encoded, encoding='utf-8'):
    return int(encoded.decode(encoding))

# Pay to Public Key Hash Structure
# https://en.bitcoinwiki.org/wiki/Pay-to-Pubkey_Hash#Pay-to-PublicKey_Hash_Example
class Pay2PubKeyHash:
    # r_pubkey is receivers public key
    def __init__(self, r_pubkey: tuple):
        # public key hash to send to sender, encoded as base64
        self.pubkey_h = wallet.gen_fingerprint(r_pubkey[0])
        self.pubkey_h += wallet.gen_checksum(self.pubkey_h)
        self.pubkey_h = base64.b64encode(self.pubkey_h).decode('utf-8').replace('=','')
        #self.pubkey_h = hkdf(r_pubkey[0], hashf=sha512.Sha512, hashlen=64, blocklen=128,
        #                     outlen=32, keylen=66) # hash using hkdf

        


class Transaction:
    def __init__(self):
        pass
