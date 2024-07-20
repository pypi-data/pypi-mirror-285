"""
This module is for building CommandSigData
"""
from kad_py.commands.command import Command
from kad_py.commands.sig import Sig

class CommandSigData:
    """
    This module dfines an instance of CommandSigData needed for quicksign transactions
    """
    def __init__(self, cmd:Command, sigs:list[Sig]):
        self.cmd = cmd
        self.sigs = []