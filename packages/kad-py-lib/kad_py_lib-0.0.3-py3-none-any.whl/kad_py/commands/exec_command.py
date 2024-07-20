"""Module for building Exec commands"""
import json

from kad_py.commands.signer import Signer
from kad_py.commands.env_data import EnvData
from kad_py.commands.capability import Capability
from kad_py.commands.command import Command
from kad_py.config.setup import DEFAULT_NONCE
from kad_py.main.kad_py_pvt import get_public_key_from_account, hash_command

EXEC_TYPE = "exec"

class ExecCommand(Command):
    """
    This class defines an exec command
    """
    def __init__(
        self,
        sender: str,
        chain_id: str,
        gas_price: int,
        gas_limit: int,
        ttl: int,
        network_id: str,
        code: str,
        data: EnvData,
        signers: list[str]=[],
        caps: list[Capability]=[],
        nonce: str=DEFAULT_NONCE
    ):
        super().__init__(sender, chain_id, gas_price, gas_limit, ttl, network_id)
        self.code = code
        self.data = data
        self.caps = caps
        self.nonce = nonce
        self.signed_cmd = ""
        self.type = EXEC_TYPE
        self.signers = [Signer(signer, caps) for signer in signers]

    def get_cmd(self):
        """
        This function returns command data in format expected by Pact CLI for signing

        Returns:
            dict: exec command data in format expected by Pact CLI
        """

        exec_cmd_data = {
            "code": self.code,
            "data": self.data.get_env_data(),
            "nonce": self.nonce,
            "networkId": self.network_id,
            "publicMeta": self.cmd_meta.get_cmd_meta(),
            "signers": self.get_signers_for_cli(),
            "type": self.type,
        }

        signable_cmd = {
            "cmd": exec_cmd_data,
            "pubKey": get_public_key_from_account(self.cmd_meta.get_cmd_meta()["sender"]) #TODO: make sure correct
        }

        return signable_cmd

    def get_cmd_for_api(self):
        """
        This function restructures the command to a format compatible with the Pact API

        Returns:
            dict: contains data defining the exec command
        """
        cmd = {
            "meta": self.cmd_meta.get_cmd_meta(),
            "networkId": self.network_id,
            "nonce": self.nonce,
            "payload": {
                "exec": {
                    "code": self.code,
                    "data": self.data.get_env_data()
                }
            },
            "signers": self.get_signers_for_api()
        }
        # meta = self.cmd_meta.get_cmd_meta()
        # cmd = {
        #     "code": self.code,
        #     "caps": [cap.get_capability() for cap in self.caps],
        #     "sender": meta["sender"],
        #     "gasLimit": meta["gasLimit"],
        #     "gasPrice": meta["gasPrice"],
        #     "chainId": meta["chainId"],
        #     "ttl": meta["ttl"],
        #     "envData": self.data.get_env_data(),
        #     "signingPubKey": get_public_key_from_account(meta["sender"]),
        #     "networkId": self.network_id
        # }

        cmd_hash = hash_command(cmd)

        cmd_payload = {
            "hash": cmd_hash,
            "sigs": [], #TODO: build signing functionality
            "cmd": json.dumps(cmd)
        }

        return cmd_payload

    def format_cmd_for_cli(self):
        """
        This function restructures the command to a format compatible with the Pact CLI

        Returns:
            dict: contains data defining the exec command
        """
        cmd_dict = json.loads(self.signed_cmd)
        
        cmd = cmd_dict["cmds"][0]
        cmd["sigs"] = [cmd["sigs"][i]["sig"] for i in cmd["sigs"]]

        return cmd

    # SETTERS
    def set_signed_cmd(self, signed_cmd):
        """
        This function
        """
        self.signed_cmd = signed_cmd
    
    # GETTERS
    def get_signers_for_cli(self):
        """
        This function
        """
        if len(self.signers) > 0:
            return [signer.get_signer_for_cli() for signer in self.signers]
        else:
            return self.signers

    def get_signers_for_api(self):
        """
        This function
        """
        if len(self.signers) > 0:
            return [signer.get_signer_for_api() for signer in self.signers]
        else:
            return self.signers

    def get_signed_cmd(self):
        """
        This function
        """
        return self.signed_cmd

    def get_type(self):
        """
        This function
        """
        return self.type
