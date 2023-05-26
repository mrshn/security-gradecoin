import threading
import base64
# import requests
import hashlib
import jwt
import time

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Hash import SHA256
from datetime import datetime
import json


from transaction import Transaction
from rsa_key_util import RsaUtil


transaction_url = "https://gradecoin.xyz/transaction"
register_url = "https://gradecoin.xyz/register" 


class SatoshiNakamoto:
    def __init__(self):
        self.my_source_address = "57330b4ffe02348404ee878be5938d4558fb7883ced4d9186b6fba11693c137d"
        self.my_rsa_util = RsaUtil()
        self.gradecoin_public_key = self.my_rsa_util.read_gradecoin_public_key()
        
        # Extracting the public key in PEM format
        self.my_RSA_Pem_Public_key = self.my_rsa_util.get_my_RSA_Pem_Public_key()

        # Extracting the public key in PEM format
        self.my_RSA_Pem_Private_key = self.my_rsa_util.get_my_RSA_Pem_Private_key()
        print(self.my_RSA_Pem_Public_key)
        print("anan")
        print(self.my_RSA_Pem_Private_key)

        self._generate_jwt_token()
        self.transaction_dicts = {}


    def start(self):
        print("Satoshi Nakamoto is alive...")
        self.register()

        # while True:

            # agent = Slaviu(client_socket)
            # agent.start()

    def _post_call(self,url,json,headers):
        # TODO: check if the field is json or data
        response = requests.post(url, json=json, headers=headers)
        print(response)
        response_data = response.json()
        print(response_data)
        if response.status_code == 200:
            print("Registration successful!")
            print("Response:", response.text)
        else:
            print("Registration failed. Status code:", response.status_code)
            print("Response:", response.text)
        return response

    def _get_call(self,url,headers):
        response = requests.get(url, headers=headers)
        print(response)
        response_data = response.json()
        print(response_data)
        if response.status_code == 200:
            print("Registration successful!")
            print("Response:", response.text)
        else:
            print("Registration failed. Status code:", response.status_code)
            print("Response:", response.text)
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
         
        headers = {}

        self._post_call(register_url,auth_request,headers)
        


    def _generate_jwt_token(self, tha="hash_of_payload" ):

        if(self.jwt_token != None):
            decoded_token = jwt.decode(self.jwt_token, self.my_RSA_Pem_Public_key, algorithms=["RS256"])
            issued_at = decoded_token.get('iat')  
            expiration_time = decoded_token.get('exp')  

        payload = {
            "tha": tha,
            "iat": int(time.time()),  
            "exp": int(time.time()) + 3600  # Expiration Time (1 hour from now)
        }

        private_key_pem = self.my_rsa_util.get_my_RSA_Pem_Private_key()
        self.jwt_token = jwt.encode(payload, private_key_pem, algorithm='RS256')


    def get_transaction(self):

        headers = {
            "Authorization": f"Bearer {self.jwt_token}"
        }


        response = self._get_call(transaction_url, headers=headers)
        response_data = response.json()

        # Convert the response data to Python objects
        source =""
        transactions = {}
        for transaction_id, transaction_data in response_data.items():
            transaction = Transaction.from_dict(transaction_data)
            source = transaction.source
            transactions[transaction_id] = transaction

        # Access the transactions by their IDs
        for transaction_id, transaction in transactions.items():
            print(f"Transaction ID: {transaction_id}")
            print(f"Source: {transaction.source}")
            print(f"Target: {transaction.target}")
            print(f"Amount: {transaction.amount}")
            print(f"Timestamp: {transaction.timestamp}")
            print()

        # Convert the Transaction objects to dictionaries using the ID as a key
        self.transaction_dicts = {}
        
        for transaction_id, transaction in transactions.items():
            self.transaction_dicts[transaction_id] = transaction.to_dict()


    def get_transaction_source(self):
        if list(self.transaction_dicts.keys()).__len__ > 0:
            return list(self.transaction_dicts.keys())[0]
        return None    

    def create_transaction(self):

        source = self.get_transaction_source()
        if source is None:
            return None
        
        transaction_data = {
            'source': self.my_source_address,
            'target': source,
            'amount': 1,
            'timestamp': datetime.now().isoformat()
        }

        transaction_data_json = json.dumps(transaction_data)
        transaction_data_json = transaction_data_json.replace(" ", "")
        # transaction_data_json = """{"source":"57330b4ffe02348404ee878be5938d4558fb7883ced4d9186b6fba11693c137d","target":"9bd3b2539516692aabd605ee7ee77737b28e232d5d919325c0a60f05026fc96c","amount":1,"timestamp":"2023-05-25T22:56:41.238319860"}"""
        anan = transaction_data_json.encode()
        print(anan)
        print("allah")
        md5_hash = hashlib.md5(transaction_data_json.encode()).hexdigest()
        print(md5_hash)
        # md5_hash = "846cad0cabc83556b1649d1fa92e958c"
        print(md5_hash)
      
        self._generate_jwt_token(tha=md5_hash)

        headers = {
            "Authorization": f"Bearer {self.jwt_token}"
        }

        response = self._post_call(transaction_url, transaction_data_json, headers)
        # response = requests.post(url, data=transaction_data_json, auth=BearerAuth(jwt_token))









# Response: {"res":"Success","message":"You have authenticated to use Gradecoin with identifier 57330b4ffe02348404ee878be5938d4558fb7883ced4d9186b6fba11693c137d"}



# class BearerAuth(requests.auth.AuthBase):
#     def __init__(self, token):
#         self.token = token
#     def __call__(self, r):
#         r.headers["authorization"] = "Bearer " + self.token
#         return r