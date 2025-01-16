from print_service import Printer
print = Printer(__file__).print
from client import Client
from authentication import AuthenticationService

class SessionManager:
    def __init__(self, authenticationService: AuthenticationService):
        self.authenticationService = authenticationService
        self.token_sessions = {}  # Maps token to sid

    def create_session(self, token: str, sid: str) -> Client:
        """
        Create or update a session by authenticating the client using the provided token.
        If the token is already associated with a different sid, update the sid.
        """
        # Authenticate client with the token
        client: Client = self.authenticationService.decrypt_token(token)

        if not client:
            print(f"Authentication failed for token {token}")
            return None

        # Check if the token is already associated with a different SID
        existing_sid = self.token_sessions.get(token)

        if existing_sid:
            if existing_sid != sid:
                # Token is associated with a different SID, update the sid
                print(f"Token {token} is associated with a different SID ({existing_sid}). Updating to new SID {sid}.")
                self.token_sessions[token] = sid
            else:
                print(f"Token {token} is already associated with SID {sid}. No update needed.")
        else:
            # If the token is not yet associated with any SID, create a new association
            print(f"Creating new session for token **** with SID {sid}")
            self.token_sessions[token] = sid

        print(f"Session created/updated for token **** with SID {sid}")
        return client

    def get_session(self, token: str) -> str:
        """
        Retrieve the SID associated with a given token.
        """
        return self.token_sessions.get(token)

    def get_session_by_sid(self, sid: str) -> str:
        """
        Retrieve the TOKEN str from the SID str
        """
        # Iterate through the dictionary to find the token corresponding to the given sid
        for token, session_sid in self.token_sessions.items():
            if session_sid == sid:
                return token
        # If no matching SID is found, return None or a suitable message
        print(f"No session found for SID {sid}")
        return None

    def close_session(self, token: str):
        """
        Close a session by removing the token and associated SID.
        """
        if token in self.token_sessions:
            sid = self.token_sessions.pop(token)
            print(f"Session closed for token {token} with SID {sid}")
        else:
            print(f"Session with token {token} not found.")

    def list_active_sessions(self) -> list:
        """
        List all active sessions (token, sid).
        """
        return list(self.token_sessions.items())
