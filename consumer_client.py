from typing import Dict
from print_service import Printer
# Initialize logging and socketio
print = Printer(__file__).print
import socketio


sio = socketio.Server()

# Dictionary to maintain active clients
clients: Dict[str, str] = {}

def consumer_client(sio: socketio.Server):

    
    @sio.event
    def register_client(sid, client_identifier):
        """
        Registers a client with a unique identifier.
        If the client reloads the page, update their session.
        """
        if client_identifier in clients:
            # Update session for existing client
            print(f"web client reconnected: {client_identifier} (Old SID: {clients[client_identifier]}, New SID: {sid})")
        else:
            # Register new client
            print(f"new web client registered: {client_identifier} (SID: {sid})")
        
        # Map the unique client identifier to the current session ID
        clients[client_identifier] = sid



    return sio
