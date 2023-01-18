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

# wallet is senders wallet
# wallet address is receiver's wallet address
# amount of amount to send
class TransactionSend(wallet.Wallet):
    def __init__(self, wallet, wallet_addrs, amount): # checksum is the first 4 bytes of the wallet
        super().__init__()
        self.wallet = wallet
        self.wa = wallet_addrs
        self.
