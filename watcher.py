import hashlib
import threading
import requests

transaction_url = "https://gradecoin.xyz/transaction"


class Watcher(threading.Thread):
    def __init__(self,result_queue,stop_event):
        super(Watcher, self).__init__(daemon=True)
        self.result_queue = result_queue
        self.event = stop_event

    def watch_transactions(self):
        response = requests.get( transaction_url, headers={} )
        response_data = response.json()
        if response_data.items().__len__() <10:
            return False
        return True

    def run(self):
        
        while self.watch_transactions():
            if self.event.is_set():
                return
        self.event.set()
        self.result_queue.put((1 , 0))
        print("Watcher is dead")
        
