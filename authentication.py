from print_service import Printer
print = Printer(__file__).print

from client import Client

import json
from cryptography.fernet import Fernet

# Initialize Fernet key for encryption/decryption (keep it secure)
# This key should be stored securely, not hardcoded in production.
SECRET_KEY = b'efgBJL1_vx-5hb2Dgh6fj3k81OBU6aZDfcBjkL5MfyE=' # Replace this with a securely generated key
cipher_suite = Fernet(SECRET_KEY)

class AuthenticationService:
    # Decrypt the token and extract the role from it
    @staticmethod
    def decrypt_token(client_as_a_token: str) -> Client:
        try:
            # Decrypt the token
            client_as_a_string = cipher_suite.decrypt(client_as_a_token.encode()).decode()
            # Load the JSON data (it should contain the role)
            #TODO: Avoid ram allocation of this object
            client: Client = Client(**json.loads(client_as_a_string))
            return client
        except Exception as e:
            print(f"Error decrypting token: {e}")
            return None
        
    @staticmethod
    def generate_encrypted_token(client:Client):
        client_as_string = json.dumps(client.__json__())
        client_as_a_token = cipher_suite.encrypt(client_as_string.encode())
        return client_as_a_token.decode()

if __name__ == "__main__":
    clientString: str = AuthenticationService.generate_encrypted_token(Client('jota','develper'))
    print('client str', clientString)

    print('clientAgain', AuthenticationService.decrypt_token(clientString).__json__())