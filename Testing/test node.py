"""
 * A Blockchain
 * Copyright (C) 2022 Taha Canturk
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.

 * Author: Taha Canturk
 *  Github: kibnakamoto
 *  Project: Blockchain
 *    Date: Jan 31 - 2023
 *     Software Version: 1.0
"""

# run this code in path blockchain/node/test.py
# If using Windows - Turn off Windows Defender for public connections
# use two computers running in the same network
# don't forget to change the ip address in line 19 to whatever you are connecting to
# the other file will have receiver

# To test server / client connections, use node/server.py and node/client.py, don't forget to change the IP addresses accordingly

# if ui.py works, there is no need for this

import time
from p2p import P2P

node = P2P(port=8333, debug=True)
#node.new_ip('192.168.0.19')

# sender side
node.sender(8333, 5)
while True:
    cli, addr = node.accept()
    node.send('Hello', addr)
    node.disconnect(addr)
    break

# receiver side
val = node.receiver("192.168.0.24", 8333)
print(val)
# to check if port is open on external ip: https://www.yougetsignal.com/tools/open-ports/
# hotspot external 199.7.157.21

""" terminate port in linux
kill -9 $(lsof -t -i:8333 -sTCP:LISTEN)
"""