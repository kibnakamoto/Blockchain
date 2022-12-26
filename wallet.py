# the wallet structure and account stuff of buyers

import secrets
import ecc.sha512

# account information
class Account:
    def __init__(self):
        self.user_id =  None # anonymous user id. can be changed at any time to maintain anonymity, length is 64 bytes
        self.wallet_address = None # wallet address that is the key for the wallet
    
    def create_user_id(self, userid=None):
        if userid != None and userid:
            self.user_id = userid
