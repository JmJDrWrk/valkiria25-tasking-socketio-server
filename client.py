class Client:
    def __init__(self, id: str, role: str):
        self.id = id
        self.role = role

    def __json__(self):
        return {"id": self.id, "role": self.role}

from typing import List

class Worker(Client):
    def __init__(
        self,
        id: str,
        role:str,
        # exclusive properties
        os:str,
        max_load: dict,
        allow_balance: bool, #Allows server to assing to it tasks
        service_keys: List[dict] #Json representation of a list of services
    ):
        super().__init__(id=id, role="worker")

        self.os = os
        self.max_load = max_load
        self.allow_balance = allow_balance
        self.service_keys = service_keys

    def __json__(self):

        data = super().__json__()
        data.update(
            {
                "os": self.os,
                "max_load": self.max_load,
                "allow_balance": self.allow_balance,
                "service_keys": self.service_keys
            }
        )
        return data


class WebClient(Client):
    def __init__(
        self,
        id: str,
        role:str,
        # exclusive properties
        business_logic: dict, # Can be loaded form db to include payments/plans or whatever...

    ):
        super().__init__(id=id, role="webclient")
        self.business_logic = business_logic

    def __json__(self):

        data = super().__json__()
        data.update(
            {
                "business_logic": self.business_logic
            }
        )
        return data

"""Like a worker but much more simpler for single script executions"""
class UnbalancedService(Client):

    def __init__(self,
                 id:str,
                role:str,

                 async_supported:bool,
                 max_load:dict,
                 name:str

                 ):
        
        super().__init__(id=id, role="service")
        
        self.async_supported = async_supported
        self.max_load= max_load
        self.name = name

    def __json__(self):

        data = super().__json__()
        data.update(
            {
                "async_supported": self.async_supported,
                "max_load": self.max_load,
                "name": self.name
            }
        )
        return data