"""This module defines a Sig object when signing commands over the Kadena Blockchain"""
from kad_py.main.kad_py_pvt import get_public_key_from_account
class Sig:
    """
    This class defines a sig needed to execute commands on the Kadena Blockchain
    """
    def __init__(self, cmd_hash: str, sig: str, public_key: str):
        self.cmd_hash = cmd_hash
        self.sig = sig
        self.public_key = get_public_key_from_account(public_key)
    
    def get_sig(self):
        """
        This function returns an object that defines the sig

        Returns:
            dict: object containing data defining the sig
        """
        return {
            "hash": self.cmd_hash,
            "sig": None, #TODO: check pact lang js for attachSig()
            "public_key": self.public_key
        }
    
    def get_sig_for_quicksign(self):
        """
        This function returns an object defining a sig for quicksign

        Returns:
            dict: object containing data defining the sig for quicksign
        """
        return {
            "pubKey": self.public_key,
            "sig": None
        }
