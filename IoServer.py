# @@ Logging
from print_service import Printer
print = Printer(__file__).print
from print_service import _print, colorama, Fore, Back, Style

import socketio
import eventlet
import time

import threading

# Inicializar Socket.IO
sio: socketio.Server = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)


# Cargar el contexto SSL
import ssl
context = ssl.SSLContext(ssl.PROTOCOL_TLS)
context.load_cert_chain(certfile='/etc/letsencrypt/live/bluejims.com/fullchain.pem', 
                        keyfile='/etc/letsencrypt/live/bluejims.com/privkey.pem')


from authentication import AuthenticationService, Client
authenticationService = AuthenticationService()

from session_manager import SessionManager
sessionManager = SessionManager(authenticationService)

@sio.event
def connect(sid, environ, auth):
    # print(f'sid {sid} e {environ}')

    client: Client = sessionManager.create_session(auth.get('token'))

    if not client:
        return False
    
    print('client connection allowed')
    
    

# Example function for token validation
def validate_token(token):
    # Replace with your token validation logic
    return token == "expected-token"

# Example function to determine client role
def determine_client_role(environ):
    # Example: Role determined by a query parameter or header
    return environ.get('QUERY_STRING', 'unknown')

@sio.event
def disconnect(sid):
    print('Disconnect is doing nothing, pay attention to this if note POLTERGEIST BEHAVIOR')
    # print(f"Attempting to disconnect {sid}")
    # # Reverse lookup in controllers
    # for name, session in list(Auth.controllers.items()):
    #     if session.get_sid() == sid:
    #         del Auth.controllers[name]
    #         print(f"Controller {name} disconnected (sid: {sid})")
    #         break
    # # Reverse lookup in controlled
    # for name, session in list(Auth.controlled.items()):
    #     if session.get_sid() == sid:
    #         del Auth.controlled[name]
    #         print(f"Controlled device {name} disconnected (sid: {sid})")
    #         break
    # print(f"Current state of controllers: {Auth.controllers}")
    # print(f"Current state of controlled devices: {Auth.controlled}")

from task_manager import TaskManager, Task
task_manager: TaskManager = TaskManager()

from load_balancer import LoadBalancer
load_balancer: LoadBalancer = LoadBalancer(task_manager)

from clients_handler import WebClients
web_clients: WebClients = WebClients(task_manager)

from workers_handler import RemoteLocalClients
remote_local_clients: RemoteLocalClients = RemoteLocalClients(task_manager)

from client_manager import ClientManager
client_manager = ClientManager()

web_clients.forward(sio)

remote_local_clients.forward(sio)

# # Start task processing in a separate thread
# def start_task_processing():
#     load_balancer.keepProcessing(sio)  # Start the keepProcessing method in a background thread

# # Call the start_task_processing function in a new thread to keep processing tasks
# task_processing_thread = threading.Thread(target=start_task_processing, daemon=True)
# task_processing_thread.start()


if __name__ == "__main__":
    try:
        print('\n\n\n@@ Starting Main Server @@\n\n')
        colorama.init()
        _print(Fore.CYAN + '> server encrypted usins SSL keys \n> property of Jaime Roman Gil\n' + Style.RESET_ALL)
        
        server = eventlet.wrap_ssl(
            eventlet.listen(('0.0.0.0', 4999)),
            certfile='/etc/letsencrypt/live/netofcomputers.com/fullchain.pem',
            keyfile='/etc/letsencrypt/live/netofcomputers.com/privkey.pem',
            server_side=True
        )
        eventlet.wsgi.server(server, app)
    except Exception as e:
        print("Error In Main Server", e)
        time.sleep(5 * 60)
