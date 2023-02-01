# copy paste the following onto the end of transaction.py
# run using 'python3 transaction.py' in the terminal

""" for testing wallet verification and transaction making """
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
if verified_wallet_connection:
    # continue with transaction
    # Bob sends transaction to Alice
    wlt1.balance = 50
    transaction = Transaction(wlt1, wlt.pubkey, 1.0, 0)
    transaction.add_transaction()
    transaction.save()

    # alice receives transaction
    print(tx_receiver(wlt, wlt1.pubkey, 5.0, 0, transaction.tx_hash))
    print("checksum: ", checksum)