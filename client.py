class Client:
    def __init__(self,
                 id: str,
                 role: str
                 ):
        self.id = id
        self.role = role
    
    def __json__(self):
        return {
            "id" : self.id,
            "role" : self.role
        }