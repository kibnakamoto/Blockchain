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
import os

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

# receiver sends checksum
def start_receiver(port:int=8333) -> None:
    ip_label = tk.Label(window, text="receiver ip:")
    ip_label.pack()
    ip_entry = tk.Entry(window)
    ip_entry.pack()
    def accept():
        ip = ip_entry.get()
        node.receiver(ip, 8333) # get public key of sender as wallet.b64
        w = curves.Weierstrass(constants.CURVE.p, constants.CURVE.a, constants.CURVE.b)
        sender = curves.Curve(constants.CURVE)
        sender.get_prikey()
        sender.get_pubkey()
        node.client.sock.send(wallet.b64(sender.pub_k)) # sends from client. Send from server
        cli, addr = node.accept()
        received = wallet.b64_d(node.last_received.decode('utf-8'))
        a_shared_sec = w.multiply(received,sender.pri_k)[0]
        a_shared_sec = ecc.hkdf(a_shared_sec)
        checksum, ciphertext = wlt.secure_com_sender(a_shared_sec)
        print("checksum:", checksum)
        print("ciphertext:", ciphertext)
        print("shared secret:", a_shared_sec)
        print("public key of sender", received)
        node.client.sock.send(ciphertext, addr)
        time.sleep(0.1)
        node.client.sock.send(checksum, addr)
        print("ciphertext sent")
        ip_entry.destroy()
        ip_label.destroy()
        get_ip.destroy()
    get_ip = tk.Button(window, text="enter", command=accept)
    get_ip.pack()

# start sender node
# ip: ip of sender
# port: port of connection
def start_sender(port:int=8333):
    ip_label = tk.Label(window, text="sender ip:")
    ip_label.pack()
    ip_entry = tk.Entry(window)
    ip_entry.pack()
    def accept():
        w = curves.Weierstrass(constants.CURVE.p, constants.CURVE.a, constants.CURVE.b)
        sender = curves.Curve(constants.CURVE)
        sender.get_prikey()
        sender.get_pubkey()

        # send public key to receiver
        node.sender(port, 5)
        while True:
            cli, addr = node.accept()
            node.send(wallet.b64(sender.pub_k), addr)
            node.last_received = node.server.sock.recv(425) # get public key of sender as wallet.b64
            time.sleep(1) # wait a second for receiver to calculate 
            ciphertext = node.server.sock.recv(32) # get ciphertext as base16
            checksum = node.server.sock.recv(8) # get base64 checksum
            break
        b_shared_sec = w.multiply(wallet.b64_d(node.last_received.decode('utf-8')), sender.pri_k)[0]
        b_shared_sec = ecc.hkdf(b_shared_sec)

        # verify checksum to make sure connection is secure
        verified_wallet_connection = wlt.secure_com_receiver(b_shared_sec, ciphertext.decode('utf-8'), checksum)
        if not verified_wallet_connection:
            node.client.stop()
            node.server.quit_server()
            raise ConnectionError("NOT SECURE: ABORTED")
        else:
            print("verified, wallet connection secure. Transaction can be securely made")
        ip_entry.destroy()
        ip_label.destroy()
        get_ip.destroy()
    get_ip = tk.Button(window, text="enter", command=accept)
    get_ip.pack()

# stop node connection
def stop_connection():
    label = tk.Label(window, text="ip of other node:")
    label.pack()
    entry = tk.Entry(window)
    entry.pack()
    def stop():
        try:
            node.disconnect(entry.get())
        except KeyError:
            pass
        label.destroy()
        entry.destroy()
        verify_input.destroy()
    verify_input = tk.Button(window, text="enter", command=stop)
    verify_input.pack()

# send transaction
def send_tx():
    var =tk.IntVar()
    var.set(1.0)
    spin = Spinbox(window, from_=0.1, to=wlt.balance, width=5, textvariable=var)
    spin.pack()

    def accept():
        time.sleep(1)
        pubk = wallet.b64_d(node.server.sock.recv(425).decode('utf-8')) # get b64 wallet address as ec point
        amount = int(spin.get())
        block_index = len(next(os.walk('blocks'))[1])
        tx = transaction.Transaction(wlt, pubk, amount, block_index)
        tx.add_transaction()
        tx.save()
        node.server.cli.send(str(amount).encode('utf-8') + b' ' + tx.tx_hash.encode('utf-8') + b' ' + wlt.wallet_address) # tx info to connected node
        verify_input.destroy()

    verify_input = tk.Button(window, text="send transaction", command=accept)
    verify_input.pack()

def receive_tx():
    def accept():
        node.client.sock.send(wlt.wallet_address)
        buffer = node.receive().decode('utf-8')
        buffer = buffer.split(' ')
        amount = int(buffer[0])
        tx_hash = buffer[1]
        pubk = wallet.b64_d(buffer[2])
        block_index = len(next(os.walk('blocks'))[1])
        print(transaction.tx_receiver(wlt, wallet.b64_d(node.last_received), amount, block_index, tx_hash))

    # alice receives transaction
    verify_input = tk.Button(window, text="send transaction", command=accept)
    verify_input.pack()

# start node as blockchain node, communicate with other nodes in the network
# TODO: not defined yet
def start_node():
    pass

# start mining with specified amount of CPU threads
def start_mining():
    if os.path.getsize('mempool') == 0:
        raise Exception("mempool is empty")
    m_label = tk.Label(window, text="thread count:")
    m_label.pack()
    m_entry = tk.Entry(window)
    m_entry.pack()
    miner = mine.Mine()
    def accept():
        miner.threading_find_nonce(int(m_entry.get()))
        miner.blck.add_block(transactions=miner.blck.mempool)
        m_label.destroy()
        m_entry.destroy()
        verify_input.destroy()
    verify_input = tk.Button(window, text="enter", command=accept)
    verify_input.pack()

window.config(menu=menubar)

mining = tk.Button(window, text="mine", command=start_mining)
mining.pack()

# transaction commands
transaction_m.add_command(label='send', command=send_tx)
transaction_m.add_command(label='receive', command=receive_tx)

# wallet commands
wallet_m.add_command(label='new keys', command=wlt.new_keys)
wallet_m.add_command(label='get keys', command=get_wallet_keys)
wallet_m.add_command(label='keys', command=wallet_cred) # manually input keys
wallet_m.add_command(label='download wallet', command=download_wallet) # download wallet creds

# node commands
node_opt_m.add_command(label='sender', command=start_sender) # as sender, sends wallet checksum
node_opt_m.add_command(label='receiver', command=start_receiver) # as receiver, verifies wallet checksum
node_opt_m.add_command(label='start', command=start_node) # start connection to blockchain, contact other nodes
node_m.add_command(label='stop connection', command=stop_connection)

window.mainloop()


