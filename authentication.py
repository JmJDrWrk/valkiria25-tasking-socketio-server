from print_service import Printer
print = Printer(__file__).print

from client import Client, WebClient, UnbalancedService, Worker

import json
from cryptography.fernet import Fernet

# Initialize Fernet key for encryption/decryption (keep it secure)
# This key should be stored securely, not hardcoded in production.
SECRET_KEY = b'efgBJL1_vx-5hb2Dgh6fj3k81OBU6aZDfcBjkL5MfyE=' # Replace this with a securely generated key
cipher_suite = Fernet(SECRET_KEY)

class AuthenticationService:
    # Decrypt the token and extract the role from it

    @staticmethod
    def decrypt_token_to_json(client_as_a_token: str) -> dict:
        try:
            # Decrypt the token
            client_as_a_string = cipher_suite.decrypt(client_as_a_token.encode()).decode()
            # Load the JSON data (it should contain the role)
            #TODO: Avoid ram allocation of this object
            
            return json.loads(client_as_a_string)
        except Exception as e:
            print(f"Error decrypting token: {e}")
            return None

    @staticmethod
    def decrypt_token(client_as_a_token: str) -> Client:
        try:
            # Decrypt the token
            client_as_a_string = cipher_suite.decrypt(client_as_a_token.encode()).decode()
            # Load the JSON data (it should contain the role)
            #TODO: Avoid ram allocation of this object
            # client: Client = Client(**json.loads(client_as_a_string))
            client_as_dict = json.loads(client_as_a_string)
            client: Client = Client(id=client_as_dict['id'], role=client_as_dict['role'])
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
    clientString: str = AuthenticationService.generate_encrypted_token(WebClient(
        id="ukn",
        role='',
        business_logic={
            'plan':'free',
            'tasks_today':0
        }
    ))
    print('webclient str', clientString)


    AAAAAA: str = AuthenticationService.generate_encrypted_token(UnbalancedService(
        id="ukn",
        role='',
        max_load={},
        async_supported=False,
        name='fake-progress-processor'
    ))
    print('unbalancedService str', AAAAAA)

    # print('clientAgain', WebClient(**AuthenticationService.decrypt_token_to_json(clientString)).__json__())