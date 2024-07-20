"""Module providing functionality to convert objects to json"""

class EnvData:
    """
    This class defines the generic object that represents the envData parameter
    when executing pact commands
    """
    def __init__(self, data):
        self.data = data
    
    def get_env_data(self):
        """
        This function is a getter to return an env data object

        Returns:
            object: env data json object
        """

        return self.data


    def get_env_data_str(self):
        """
        This function is a getter to return a stringified env data object

        Returns:
            string: stringified env data json object
        """
        env_data = str(self.data)

        return env_data
