import json 

from kad_py.transactions.transaction import Transaction
from kad_py.config.constants import CLI, API
class PactSignTransaction(Transaction):
    def __init__(self, pact_signed_tx, network_id:str, sign_method:str, chain_id: str):
        super().__init__(network_id=network_id, method=sign_method, chain_id=chain_id)
        self.pact_signed_tx = pact_signed_tx

    def get_signed_cmd(self):
        return self.pact_signed_tx

    def get_cmd_w_sigs(self):
        cmd = self.pact_signed_tx["cmds"][0]
        cmd["sigs"] = [cmd["sigs"][i]["sig"] for i in range(len(cmd["sigs"]))]

        return cmd