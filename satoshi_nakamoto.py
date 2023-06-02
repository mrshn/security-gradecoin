import concurrent.futures
import queue
import base64
import requests
import hashlib
import jwt
import time
import random
import json
import threading
import os
import sys 

from json import JSONEncoder

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Hash import SHA256
from datetime import datetime


from transaction import Transaction
from rsa_key_util import RsaUtil
from slaviu import Slaviu
from watcher import Watcher


transaction_url = "https://gradecoin.xyz/transaction"
block_url = "https://gradecoin.xyz/block"
register_url = "https://gradecoin.xyz/register" 


class TransactionEncoder(JSONEncoder):
    def default(self, t):
        if isinstance(t, Transaction):
            return t.to_dict()
        return super().default(t)



class SatoshiNakamoto:
    def __init__(self):
        self.my_source_address = "dc6476290c9f42efe6b5bebead16cf067ca18b5b593d12e01bff656fa173eecc"
        # self.my_source_address = "dc6476290c9f42efe6b5bebead16cf067ca18b5b593d12e01bff656fa173eecc"
        self.my_rsa_util = RsaUtil()
        self.gradecoin_public_key = self.my_rsa_util.read_gradecoin_public_key()
        
        # Extracting the public key in PEM format
        self.my_RSA_Pem_Public_key = self.my_rsa_util.get_my_RSA_Pem_Public_key()

        # Extracting the public key in PEM format
        self.my_RSA_Pem_Private_key = self.my_rsa_util.get_my_RSA_Pem_Private_key()

        # print(self.my_RSA_Pem_Public_key)
        # print(self.my_RSA_Pem_Private_key)

        self.jwt_token = None
        self.transactions = {}
        self._generate_jwt_token()
        self.threads = []


    def start(self):
        print("Satoshi Nakamoto is alive...")
        # self.register()

        # self.get_transaction()
        # self.get_block()
        # self.create_transaction()
        while True:
            self.create_block()

            # agent = Slaviu(client_socket)
            # agent.start()

    def _post_call(self,url,json,headers):
        response = requests.post(url, data=json, headers=headers)
        print("\nResponse\n", response, "\n")
        # response_data = response.json()
        # print("\nResponse Data\n", response_data, "\n" )
        print("\nResponse Text\n", response.text, "\n" )
        print("\nResponse Status Code\n", response.status_code, "\n" )

        return response

    def _get_call(self,url,headers):
        response = requests.get(url, headers=headers)
        # print("\nResponse\n", response, "\n")
        response_data = response.json()
        # print("\nResponse Data\n", response_data, "\n" )
        # print("\nResponse Text\n", response.text, "\n" )
        # print("\nResponse Status Code\n", response.status_code, "\n" )

        return response


    def register(self):

        k_temp = get_random_bytes(16)  # 128-bit key
        iv = get_random_bytes(16)  # 128-bit IV

        # Creating P_AR JSON object with initials
        p_ar = {
            "student_id": "e237573",
            "passwd": "gJ5NwXdPJsGQnHbCLH57WhnCWph9Dpg1",
            "public_key": self.my_RSA_Pem_Public_key
        }

        # Serializing P_AR and encrypting with AES-128 CBC using k_temp
        p_ar_serialized = json.dumps(p_ar).encode("utf-8")
        cipher = AES.new(k_temp, AES.MODE_CBC, iv)
        c_ar = cipher.encrypt( pad( p_ar_serialized, AES.block_size ) )

        # Encrypting k_temp with gradecoin_public_key using RSA PKCS1 OAEP padding
        rsa_cipher = PKCS1_OAEP.new(self.gradecoin_public_key , hashAlgo=SHA256)
        key_ciphertext = rsa_cipher.encrypt(k_temp)

        c_ar_base64 = base64.b64encode(c_ar).decode("utf-8")
        key_ciphertext_base64 = base64.b64encode(key_ciphertext).decode("utf-8")
        iv_base64 = base64.b64encode(iv).decode("utf-8")

        auth_request = {
            "c": c_ar_base64,
            "iv": iv_base64,
            "key": key_ciphertext_base64
        }
        auth_data = json.dumps(auth_request)
        headers = {}
        response = self._post_call(register_url,auth_data,headers)
        return response



    def _generate_jwt_token(self, tha="hash_of_payload" ):
        payload = {
            "tha": tha,
            "iat": int(time.time()),  
            "exp": int(time.time()) + 3600  # Expiration Time (1 hour from now)
        }
        private_key_pem = self.my_rsa_util.get_my_RSA_Pem_Private_key()
        self.jwt_token = jwt.encode(payload, private_key_pem, algorithm='RS256')


    def get_transaction(self):
        response = self._get_call( transaction_url, headers={} )
        response_data = response.json()
        self.transactions = {}
        for transaction_id, transaction_data in response_data.items():
            transaction = Transaction.from_dict(transaction_data)
            self.transactions[transaction_id] = transaction
        print("Transaction Count: {}".format(len(self.transactions)))

    def is_transaction_sent(self, target_source):
        for _ , transaction in self.transactions.items():
            if(self.my_source_address == transaction.source and target_source == transaction.target):
                return True
        return False 

    def get_first_transaction_source(self):
        self.get_transaction()
        for _ , transaction in self.transactions.items():
            if(self.my_source_address != transaction.source and not self.is_transaction_sent(transaction.source)):
                return transaction.source
            if(self.my_source_address != transaction.target and not self.is_transaction_sent(transaction.target)):
                return transaction.target
        return None    

    def create_transaction(self):
        source = self.get_first_transaction_source()
        if source is None:
            return None
        transaction_json = {
            'source': self.my_source_address,
            'target': source,
            'amount': 1,
            'timestamp': datetime.now().isoformat()
        }

        transaction_data = json.dumps(transaction_json)
        transaction_data = transaction_data.replace(" ", "")
        md5_hash = hashlib.md5(transaction_data.encode()).hexdigest()
      
        self._generate_jwt_token(tha=md5_hash)
        headers = {
            "Authorization": f"Bearer {self.jwt_token}"
        }
        response = self._post_call(transaction_url, transaction_data, headers)
        return response


    def get_block(self):
        headers = {
            "Authorization": f"Bearer {self.jwt_token}"
        }
        response = self._get_call(block_url, headers=headers)
        return response

    def form_transaction_list(self):
        self.get_transaction()
        cur_transactions = list(self.transactions.values())
        if cur_transactions.__len__() > 9:
            if(cur_transactions[0].source != self.my_source_address):
                for i in range( len(cur_transactions) ):
                    if(self.my_source_address == cur_transactions[i].source):
                        my_transaction = cur_transactions[i]
                        del cur_transactions[i]
                        cur_transactions.insert(0, my_transaction)
                        return cur_transactions[:10]
                self.create_transaction()
                return self.form_transaction_list()
            else:
                return cur_transactions[:10]
        else:
            if cur_transactions.__len__() == 9:
                self.create_transaction()
                return self.form_transaction_list()
            return None

    def start_mining(self, starting_string, left, right):

        result_queue = queue.Queue()
        stop_event = threading.Event()

        for _ in range(12):
            nonce = random.randint(0, 2**32 - 1)
            miner = Slaviu(starting_string, left,nonce, right,result_queue,stop_event)
            self.threads.append(miner)
            miner.start()
        
        watcher = Watcher(result_queue,stop_event)
        self.threads.append(watcher)
        watcher.start()

        result = result_queue.get() 
        if not stop_event.is_set():
            stop_event.set()
        return result

        

    def find_blake_hash(self,formed_transaction_list, timestamp):

        nonce = random.randint(0, 2**32 - 1)
        blake_hash_value : None
        starting_string = "000000"

        temp_block_data = {
                "transaction_list": formed_transaction_list,
                "nonce": nonce,
                "timestamp": timestamp
            }
        
        temp_block_data_json = json.dumps(temp_block_data,cls=TransactionEncoder)
        temp_block_data_json = temp_block_data_json.replace(" ", "")
        
        the_nonce_str = '"nonce":'
        i = temp_block_data_json.find(the_nonce_str)
        left = temp_block_data_json[:i] + the_nonce_str
        right = temp_block_data_json[i:]
        i2 = right.find(",")
        right = right[i2:]

        return self.start_mining(starting_string, left, right)
    
        # while True:
            
        #     temp_block_data_json = left+str(nonce)+right
        #     blake_hash_value = hashlib.blake2s(temp_block_data_json.encode()).hexdigest()
        #     if(blake_hash_value.startswith(starting_string)):
        #         break
        #     nonce += 1
        
        # return (blake_hash_value , nonce)

    def get_tr_id_list(self,formed_transaction_list):
        tr_id_list = []
        for tr in formed_transaction_list:
            for tr_id, tr2 in self.transactions.items():
                if(tr2.source == tr.source and tr2.target == tr.target):
                    tr_id_list += [tr_id]
                    break
        return tr_id_list
    
    def create_block(self):
        time_stamp = datetime.now().isoformat()
        formed_transaction_list = self.form_transaction_list()
        if formed_transaction_list is None:
            return
        tr_id_list = self.get_tr_id_list(formed_transaction_list)
        (blake_hash_value , nonce) = self.find_blake_hash(tr_id_list,time_stamp)
       
        block_json = {
            "transaction_list": tr_id_list,
            "nonce": nonce,
            "timestamp": time_stamp,
            "hash": blake_hash_value
        }

        block_data = json.dumps(block_json,cls=TransactionEncoder)
        block_data = block_data.replace(" ", "")
      
        self._generate_jwt_token(tha=blake_hash_value)
        headers = {
            "Authorization": f"Bearer {self.jwt_token}"
        }

        response = self._post_call(block_url, block_data, headers)

        # sys.exit(0)
        # os.system('main.py')
        return response
