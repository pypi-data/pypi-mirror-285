"""Module for building Cont commands"""
import json 

from kad_py.commands.command import Command
from kad_py.commands.signer import Signer
from kad_py.commands.sig import Sig
from kad_py.commands.capability import Capability
from kad_py.commands.env_data import EnvData
from kad_py.config.setup import DEFAULT_NONCE
from kad_py.main.kad_py_pvt import get_public_key_from_account, hash_command

CONT_TYPE = "cont"

class ContCommand(Command):
    """
    This class defines a cont command
    """
    def __init__(
        self,
        sender: str,
        chain_id: str,
        gas_price: int,
        gas_limit: int,
        ttl: int,
        network_id: str,
        step: int,
        rollback: bool,
        data: EnvData,
        pact_tx_hash: str="",
        signers: list[str]=[],
        caps: list[Capability]=[],
        nonce: str=DEFAULT_NONCE,
        proof: str=None
    ):
        super().__init__(sender, chain_id, gas_price, gas_limit, ttl, network_id)
        self.step = step
        self.data = data
        self.caps = caps
        self.nonce = nonce
        self.proof = proof
        self.type = CONT_TYPE
        self.rollback = rollback
        self.pact_tx_hash = pact_tx_hash
        self.signers = [Signer(signer, caps) for signer in signers]
    
    def get_cmd(self):
        """
        This function returns command data in format expected by Pact CLI for signing

        Returns:
            dict: cont command data in format expected by Pact CLI
        """
        
        cont_cmd_data = {
            "pactTxHash": self.pact_tx_hash,
            "step": self.step,
            "rollback": self.rollback,
            "proof": self.proof,
            "data": self.data.get_env_data(),
            "signers": [signer.get_signer_for_cli() for signer in self.signers],
            "networkId": self.network_id,
            "publicMeta": self.cmd_meta.get_cmd_meta(),
            "nonce": self.nonce,
            "type": self.type,
        }

        signable_cmd = {
            "cmd": cont_cmd_data,
            "pubKey": get_public_key_from_account(self.cmd_meta.get_cmd_meta()["sender"])#TODO: make sure correct
        }

        return signable_cmd
    
    def get_cmd_for_api(self):
        """
        This function returns command data in format expected by Pact signing API

        Returns:
            dict: cont command data in format expected by Pact API
        """
        meta = self.cmd_meta.get_cmd_meta()
        cmd = {
            "network_id": self.network_id,
            "payload": {
                "cont": {
                    "proof": self.proof,
                    "pactId": self.pact_tx_hash,
                    "rollback": self.rollback,
                    "step": self.step,
                    "data": self.data.get_env_data()
                }
            },
            "signers": [signer.get_signer_for_api() for signer in self.signers],
            "meta": meta,
            "nonce": self.nonce
        }

        cmd_hash = hash_command(cmd)

        sigs = [Sig(cmd_hash, None, get_public_key_from_account(meta["sender"]))]
        cmd_payload = {
            "hash": cmd_hash,
            "sigs": [sig.get_sig_for_quicksign() for sig in sigs], #TODO: build signing functionality
            "cmd": json.dumps(cmd)
        }

        return cmd_payload

    #GETTERS
    def get_type(self):
        """
        This function gets the command type 

        Returns:
            string: defines the type of the command
        """
        return self.type
        