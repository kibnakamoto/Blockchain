A blockchain made in python

# How to use

1. Install dependincies using terminal command ```sh setup/dependencies.sh``` - miniupnpc isn't required since port forwarding and public IPs aren't supported yet
2. The app comes with a GUI, run ui.py
    1. the GUI has a few parts to keep in mind, the mine button starts mining. This process is similar to the process of Bitcoin mining but this is a simple file without much functionality. You have the option to mine with as many threads as you want (The limit is thread_count-1). To stop, turn off the app
    2. Wallet
        1. on the menubar, there is a wallet option. This is for wallet keys
        2. If you have a pre-existing wallet key pair that you want to use, press 'keys'
        3. If you don't have a pre-existing wallet and want to generate a new one, press 'new keys'
        4. To view the wallet key pair on a new window, press 'get keys'
        5. To download the wallet key pair onto user/wallet, press download keys
    3. How to make transactions
        1. click on node on the menubar - choose connection, then receiver (if you are the receiver node) or sender (if you are the sender node)
        2. type in the local IP of the other node on the suggested box and press enter
        3. The computer will do the rest and will notify you on the terminal whether the connection is secure or if someone intercepted it. In Docs/wallet.ipynb, the process is explained. If checksum verification fails. Then connection is insecure and you should try again
        4. Once this process is done, go to transaction on the menubar and choose amount, and fill in whatever is required. the receiver option in menu is for receiving while the sender option is for sending, Do this only after step 3 suceeds 
    

remember that while entering information: 
1. transaction hash is hexadecimal without trailing '0x'
2. public key and signatures are in base64. Convert using b64() / b64_d function in wallet.py

works in Both Windows and Linux. Should also work in Mac but isn't tested for mac

## Folder Testing - Testing Documentation/Results

Testing/'test node' - has code to test networking to prove that it will work
Testing/mempool_verification_data - code and results of everything mempool related (transactions - getting data - ownership verification - merkle-tree - etc)

Networking Trouble-shooting tip:

If OS is windows, disable windows defender which blocks the connections

## Folder Docs - Documentation

network.ipynb briefly explains how the communication happens

The other files explain what happens in the files. e.g. block.ipynb explains what happens in block.py

MerkleTree.pdf is the IPO of scope document
merkletree.ipynb is the pseudo-code of the scope document

Peter is the person who made the Merkle Tree using the pseudo-code and IPO I provided

## Folder ecc - Elliptic Curve Cryptography

ecc is the elliptic curve cryptography package that I wrote over the summer. It has a benchmark test. Feel free to run.
I am using this for cryptographic purposes of blockchain

## Folder user - personal user information
This information is private to only the user, the private key shouldn't be published since it proves ownership of the cryptocurrency

prev_transactions.json - previous transactions of the user. These are previous transactions where user was the sender

rtransactions.json - received transactions, where the proof of ownership is known. Has private keys that let you generate a signature which proves that you are the owner

## mempool

memory pool of transactions

includes:

transaction-hash + timestamp + block-index + previous-transaction-hash + previous-transaction-block-index + public-key + signature + signature-message-hash + amount

## contact.txt - contact information

For contacting me in a low-level. Manually encrypting and communicating

## LICENCE - open-source Program licenced

GNU Affero General Public Licence - Version 3

