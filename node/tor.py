"""
 * Blockchain
 * Copyright (C) 2022 Taha Canturk

 * Author: Taha Canturk
 *  Github: kibnakamoto
 *  Project: Blockchain
 *    Date: Jul 22 2023
 *     Software Version: 1.0
"""

# Tor circuit connections on the blockchain

import subprocess
import time
import requests
from fake_useragent import UserAgent


# start tor
def torify() -> str:
    subprocess.call(["sh", "start_tor.sh"])
    
    proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }
    time.sleep(1)
    headers = { 'User-Agent': UserAgent().random }
    for _ in range(3): # try three times before quitting
        try:
            new_ip = requests.get('https://ident.me', proxies=proxies, headers=headers, timeout=3).text
            break
        except ConnectionError:
            continue
    return new_ip

# quit tor
def detorify() -> str:
    subprocess.call(["sh", "stop_tor.sh"])
    new_ip = requests.get('https://ident.me', timeout=5).text
    return new_ip
