import multiprocessing

from collections import deque

import constants
import block
import merkletree

class Mine:
    def __init__(self):
        self.hashes, pubks, signatures, m_hashes, verified = merkletree.get_mempool_verification_data()
        self.nonce = None
        self.block_hash = None

        # eliminate transactions if their signatures aren't verified
        i = 0
        while self.hashes and i < len(self.hashes):
            if not verified[i]:
                del verified[i]
                del m_hashes[i]
                del signatures[i]
                del pubks[i]
                del self.hashes[i]
            i += 1

    # TODO: verify if previous transaction exists
    def verify_prevs() -> NotImplemented:
        pass

    
    # does the actual mining by calculating the nonce and block header hash
    def find_nonce(self) -> None:
        while True:
            self.nonce = block.gen_nonce()
            self.blck = block.Block(self.nonce, self.hashes)
            if(int(self.blck.block_hash, 16) < constants.target):
                break
        self.block_hash = self.blck.block_hash

    # find nonce using multi-threading
    # t: thread count
    def threading_find_nonce(self, t:int=1) -> None:
        self.threads = deque(maxlen=t)
        count = multiprocessing.cpu_count()
        if t >= count:
            t = count-1
        for i in range(t):
            thread = multiprocessing.Process(target=self.find_nonce, name=i)
            self.threads.append(thread)
            thread.start()
        
        terminate_signal = False
        while not terminate_signal:
            for thread in self.threads:
                thread.join(timeout=0)
                if self.block_hash != None:
                    thread.terminate()
                    terminate_signal = True
        self.blck.add_block(transactions=self.hashes)