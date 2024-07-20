"""Module providing utility for getting time data"""
import time

from kad_py.config.setup import DEFAULT_SENDER, DEFAULT_CHAIN_ID, \
    DEFAULT_GAS_PRICE, DEFAULT_GAS_LIMIT, DEFAULT_TTL

class CommandMetadata:
    """
    This class defines the parameters that the command is executed with on the Kadena blockchain
    """
    def __init__(
        self, 
        sender:str=DEFAULT_SENDER, 
        chain_id:str=DEFAULT_CHAIN_ID, 
        gas_price:int=DEFAULT_GAS_PRICE, 
        gas_limit:int=DEFAULT_GAS_LIMIT, 
        ttl:int=DEFAULT_TTL
    ):
        self.ttl = ttl
        self.sender = sender
        self.chain_id = chain_id
        self.gas_price = gas_price
        self.gas_limit = gas_limit
        self.creation_time = round(time.time(), 2)
    
    def get_cmd_meta(self):
        """
        This function is a getter that returns the metadata in a single dict object

        Returns:
            dict: object containing command metadata
        """
        meta = {
            "chainId": self.chain_id,
            "creationTime": round(time.time(), 0),
            "gasLimit": self.gas_limit,
            "gasPrice": self.gas_price,
            "sender": self.sender,
            "ttl": self.ttl
        }

        return meta
    