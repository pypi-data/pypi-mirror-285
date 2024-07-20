"""
This module defines the functionality of a capability, needed by some
contracts and functions that are called on the Kadena blockchain
"""
class Capability:
    """
    This class defines a capability needed for successful transaction execution
    """
    def __init__(self, role:str, description:str, name:str, args:list):
        self.role = role
        self.description = description
        self.name = name
        self.args = args
    
    def get_capability(self):
        """
        This function returns object containing data defining the capability

        Returns:
            dict: object defining capability
        """
        cap = {
            "role": self.role,
            "description": self.description,
            "name": self.name,
            "args": self.args
        }

        return cap
    
    def get_capability_api(self):
        """
        This function returns object containing data defining the capability

        Returns:
            dict: object defining capability
        """
        cap = {
            "role": self.role,
            "description": self.description,
            "cap": {
                "name": self.name,
                "args": self.args
            }
        }

        return cap
