import hashlib
import threading

class Slaviu(threading.Thread):
    def __init__(self, starting_string, left, nonce , right,result_queue,stop_event):
        super(Slaviu, self).__init__(daemon=True)
        self.starting_string = starting_string
        self.left = left
        self.right = right
        self.nonce = nonce
        self.result_queue = result_queue
        self.event = stop_event

    def run(self):
        
        while True:
            
            temp_block_data_json = self.left+str(self.nonce)+self.right
            blake_hash_value = hashlib.blake2s(temp_block_data_json.encode()).hexdigest()
            if(blake_hash_value.startswith(self.starting_string)):
                print("I am finished")
                if self.event.is_set():
                    break
                else:
                    self.result_queue.put((blake_hash_value , self.nonce))
                return  0
            self.nonce += 1
            if self.event.is_set():
                break
        
        print("I am dead")
        
