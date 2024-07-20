"""Module for building Signers"""
from kad_py.commands.capability import Capability
from kad_py.main.kad_py_pvt import get_public_key_from_account

class Signer:
    """
    This class defines a signer needed when executing commands on the Kadena Blockchain
    """
    def __init__(self, signer_wallet:str, caps:list[Capability]=[]):
        self.public_key = get_public_key_from_account(signer_wallet)
        self.secret_key = "" #TODO: verify this is needed
        self.caps = caps
    
    def get_signer_for_cli(self):
        """
        This function returns signer in format expected by CLI
        """
        clist = [cap.get_capability() for cap in self.caps]
        
        signer = {
            "public": self.public_key,
            # "secret_key": self.secret_key,
            "caps": clist
        }
        
        return signer
    
    def get_signer_for_api(self):
        """
        This function returns signer in format expected by API
        """
        clist = [cap.get_capability_api() for cap in self.caps]

        signer = {
            "pubKey": self.public_key,
            "clist": clist
        }

        return signer
