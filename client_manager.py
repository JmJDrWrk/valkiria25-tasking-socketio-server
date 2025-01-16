# ClientManager Class
class ClientManager:
    def __init__(self):
        self.clients = {}  # Dictionary to store clients: {sid: {'role': role, 'data': data}}

    def add_client(self, sid, role, **kwargs):
        self.clients[sid] = {'role': role, **kwargs}
        print(f"Added client {sid} with role {role}")

    def remove_client(self, sid):
        if sid in self.clients:
            del self.clients[sid]
            print(f"Removed client {sid}")
        else:
            print(f"Attempted to remove non-existent client {sid}")

    def get_client(self, sid):
        return self.clients.get(sid)

    def get_all_clients(self):
        return self.clients

    def get_clients_by_role(self, role):
        return {sid: data for sid, data in self.clients.items() if data.get('role') == role}
