from print_service import Printer
print = Printer(__file__).print

from client import Client
from authentication import AuthenticationService

class SessionManager:
    def __init__(self, authenticationService: AuthenticationService):
        self.authenticationService = authenticationService
        self.token_sessions = {}
        self.sid_sessions = {}  

    def create_session(self, token: str) -> Client:
        """
        Create or update a session by authenticating the client using the provided token.
        If the token is already associated with an active session, update the sid.
        """
        # Authenticate client with the token
        client: Client = self.authenticationService.decrypt_token(token)

        if not client:
            return False

        if client:
            existing_sid = self.token_sessions.get(token)
            
            if existing_sid:
                # If token exists, update the sid for the existing session
                print(f"Token already associated with SID {existing_sid}. Updating to new SID {client.sid}.")
                self.sid_sessions.pop(existing_sid)  # Remove the old session from sid_sessions
                self.token_sessions[token] = client.sid  # Update the token's sid
                self.sid_sessions[client.sid] = client  # Add new sid to sid_sessions
            else:
                # If token doesn't exist, create a new session
                self.token_sessions[token] = client.sid
                self.sid_sessions[client.sid] = client

            print(f"Session created/updated for client {client.sid}")
            return client
        else:
            print(f"Authentication failed for token {token}")
            return None

    def get_client_session(self, sid: str) -> Client:
        """
        Retrieve an active client session using the session ID (sid).
        """
        return self.sid_sessions.get(sid)

    def close_session(self, sid: str):
        """
        Close a session by removing the client from active sessions.
        """
        if sid in self.sid_sessions:
            client = self.sid_sessions.pop(sid)
            self.token_sessions.pop(client.token)  # Remove the token's association with the sid
            print(f"Session closed for client {sid}")
        else:
            print(f"Session with SID {sid} not found.")

    def list_active_sessions(self) -> list:
        """
        List all active client sessions.
        """
        return list(self.sid_sessions.values())

