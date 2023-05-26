import os
from Crypto.PublicKey import RSA

gradecoin_key_file ="gradecoin.pub"
my_private_key_file = 'private_key.pem'
my_public_key_file = 'public_key.pem'

class RsaUtil:
    
    def __init__(self,):
        self.gradecoin_public_key = RSA.import_key(open(gradecoin_key_file, "rb").read())
        
        if os.path.exists(my_private_key_file) and os.path.exists(my_public_key_file):
            self.read_RSA_from_file()
        else:
            self.generate_my_RSA()
            self.read_RSA_from_file()

    def read_gradecoin_public_key(self,):
        return self.gradecoin_public_key

    def generate_my_RSA(self,):
        # Generating RSA key pair
        generated_rsa_key = RSA.generate(2048)

        with open(my_private_key_file, 'wb') as f:
            f.write(generated_rsa_key.export_key(pkcs=8))

        with open(my_public_key_file, 'wb') as f:
            f.write(generated_rsa_key.publickey().export_key(pkcs=8))


    def read_RSA_from_file(self,):

        # Read the private key from file
        with open(my_private_key_file, 'rb') as f:
            private_key_pem = f.read()
            self.private_key = RSA.import_key(private_key_pem)

        # Read the public key from file
        with open(my_public_key_file, 'rb') as f:
            public_key_pem = f.read()
            self.public_key = RSA.import_key(public_key_pem)

        # Print the keys (for demonstration purposes)
        print("Private Key:")
        print(self.private_key.export_key(pkcs=8).decode("utf-8"))
        print("\nPublic Key:")
        print(self.public_key.export_key(pkcs=8).decode("utf-8"))

    def get_my_RSA_Pem_Public_key(self,):
        return self.public_key.export_key(pkcs=8).decode("utf-8")
    
    def get_my_RSA_Pem_Private_key(self,):
        return self.private_key.export_key(pkcs=8).decode("utf-8")
    

