import json

class Transaction:
    def __init__(self, network_id:str, method:str, chain_id:str):
        self.network_id = network_id
        self.method = method
        self.chain_id = chain_id

    # GETTERS
    def get_network_id(self):
        return self.network_id
   
    def get_method(self):
        return self.method
    
    def get_chain_id(self):
        return self.chain_id