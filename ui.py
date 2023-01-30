# Graphical User Interface
import transaction
import constants
import mine
import wallet
from node import p2p
from ecc import ecc, sha512, curves

import tkinter as tk
from tkinter.ttk import *
import time

# not implemented yet
# from node import node
# from node import tor

window = tk.Tk()
window.geometry('700x500')

window.title("Blockchain")

menubar = tk.Menu(window)
transaction_m = tk.Menu(menubar, tearoff=0)
wallet_m = tk.Menu(menubar, tearoff=0)
node_m = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='transaction',menu=transaction_m)
menubar.add_cascade(label='wallet',menu=wallet_m)
menubar.add_cascade(label='node',menu=node_m) # node connections (send, receive)

node_opt_m = tk.Menu(node_m,tearoff=0)
node_m.add_cascade(label='connection', menu=node_opt_m)

# node and wallet of user
node = p2p.P2P(port=8333, debug=False)
wlt = wallet.Wallet()

# alice and bob share their public keys and come up with their shared-secret
# w = curves.Weierstrass(constants.CURVE.p, constants.CURVE.a, constants.CURVE.b)
# alice = curves.Curve(constants.CURVE)
# bob = curves.Curve(constants.CURVE)
# alice.get_prikey()
# bob.get_prikey()
# alice.get_pubkey()
# bob.get_pubkey()
# a_shared_sec = w.multiply(bob.pub_k,alice.pri_k)[0]
# b_shared_sec = w.multiply(alice.pub_k,bob.pri_k)[0]
# a_shared_sec = ecc.hkdf(a_shared_sec)
# b_shared_sec = ecc.hkdf(b_shared_sec)
# 
# 
# # Alice
# wlt = wallet.Wallet()
# wlt.new_keys()
# wlt_send = wlt.secure_com_sender(a_shared_sec)
# checksum = wlt_send[0] # base64
# ciphertext = wlt_send[1]
# 
# # send ciphertext ubytessing P2P node
# 
# # Bob
# wlt1 = wallet.Wallet()
# wlt1.new_keys()
# 
# # verify checksum to make sure connection is secure
# verified_wallet_connection = wlt1.secure_com_receiver(b_shared_sec, ciphertext.decode('utf-8'), checksum)
# if verified_wallet_connection:
#     # continue with transaction
#     # Bob sends transaction to Alice
#     wlt1.balance = 50
#     transaction = Transaction(wlt1, wlt.pubkey, 5.0, 0)
#     transaction.add_transaction()
#     transaction.save()
# 
#     # alice receives transaction
#     print(tx_receiver(wlt, wlt1.pubkey, 5.0, 0, transaction.tx_hash))
# send transaction

# if wallet exists, input wallet credentials (private and public key)
def wallet_cred() -> None:
    wind = tk.Tk()
    wind.geometry('700x500')
    wind.title("Wallet Keys")
    pk_label = tk.Label(wind, text="private key:")
    pk_label.pack()
    pk_entry = tk.Entry(wind)
    pk_entry.pack()

    uk_label = tk.Label(wind, text="public key:") # input public key as base64 as defined in wallet.b64
    uk_label.pack()
    uk_entry = tk.Entry(wind)
    uk_entry.pack()
    
    def accept():
        try:
            wlt.prikey = int(pk_entry.get()) # input private key as base 10 int
        except ValueError:
            wlt.prikey = int(pk_entry.get(), 16) # input private key as base 16 hex

        # get public key as "x|y" base64 encoded
        wlt.pubkey = wallet.b64_d(uk_entry.get())
        wlt.wallet_address = uk_entry.get()

        # delete menu
        pk_label.pack_forget()
        uk_label.pack_forget()
        pk_entry.pack_forget()
        uk_entry.pack_forget()
        wind.destroy()
        get_wallet_keys()

    verify_input = tk.Button(wind, text="enter", command=accept) 
    verify_input.pack()
    

    
# downloads wallet credentials into user/wallet
def download_wallet():
    with open("user/wallet", 'w') as f:
        f.write("prikey: ", hex(wlt.prikey), "\npubkey: ", wallet.b64(wlt.pubkey), "\n")

def get_wallet_keys(): 
    new_window = tk.Tk()
    new_window.title('wallet keys')
    new_window.geometry('750x300')
    result_text = tk.Text(new_window, height=750, width=300)
    result_text.insert(tk.END, f'prikey: {wlt.prikey}\npubkey: {wallet.b64(wlt.pubkey)}\n')
    result_text.pack()

def start_sender(port:int=8333) -> None:
    node.sender(port, 5)
    while True:
        cli, addr = node.accept()
        node.send('Hello', addr)
        break

# start receiver node
# ip: ip of sender
# port: port of connection
def start_receiver(ip:str, port:int=8333):
    node.receiver(ip, port)

# stop node connection
def stop_connection():
    node.disconnect()

window.config(menu=menubar)

# transaction commands
transaction_m.add_command(label='send', command=None)
transaction_m.add_command(label='receive', command=None)

# wallet commands
wallet_m.add_command(label='new keys', command=wlt.new_keys)
wallet_m.add_command(label='get keys', command=get_wallet_keys)
wallet_m.add_command(label='keys', command=wallet_cred) # manually input keys
wallet_m.add_command(label='download wallet', command=download_wallet) # download wallet creds

# node commands
node_opt_m.add_command(label='sender', command=start_sender) # as sender, sends wallet checksum
node_opt_m.add_command(label='receiver', command=start_receiver) # as receiver, verifies wallet checksum
node_m.add_command(label='stop connection', command=stop_connection)

window.mainloop()


