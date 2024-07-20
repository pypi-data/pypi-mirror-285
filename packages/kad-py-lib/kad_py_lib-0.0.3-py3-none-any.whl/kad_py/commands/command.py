"""
This module defines the base case for a Command that gets executed in a transaction
on the Kadena blockchain
"""
from kad_py.commands.command_metadata import CommandMetadata
from kad_py.config.setup import DEFAULT_SENDER, DEFAULT_CHAIN_ID, \
    DEFAULT_GAS_PRICE, DEFAULT_GAS_LIMIT, DEFAULT_TTL, \
    DEFAULT_NETWORK_ID

class Command:
    """
    This class is the parent class for all commands to be executed on the Kadena blockchain
    The specific command types that inherit from this class are ExecCommand and ContCommand
    """
    def __init__(
        self, 
        sender: str=DEFAULT_SENDER, 
        chain_id: str=DEFAULT_CHAIN_ID, 
        gas_price: int=DEFAULT_GAS_PRICE, 
        gas_limit: int=DEFAULT_GAS_LIMIT, 
        ttl: int=DEFAULT_TTL,
        network_id: str=DEFAULT_NETWORK_ID
    ):
        self.cmd_meta = CommandMetadata(sender, chain_id, gas_price, gas_limit, ttl)
        self.network_id=network_id
    
    # GETTERS
    def get_network_id(self):
        """
        This function returns the network ID

        Returns:
            string: ID of the network the command will be sent over
        """
        return self.network_id
    
    def get_cmd_meta(self):
        """
        This function returns the commands metadata

        Returns:
            dict: object containing the parameters the command will be executed with
        """
        return self.cmd_meta
