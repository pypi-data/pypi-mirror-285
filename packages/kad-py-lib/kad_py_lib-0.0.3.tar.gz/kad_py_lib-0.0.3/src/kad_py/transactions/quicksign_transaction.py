import json 

from kad_py.transactions.transaction import Transaction

class QuickSignTransaction(Transaction):
    def __init__(self, quicksigned_tx, network_id, sign_method: str, chain_id: str):
        super().__init__(network_id=network_id, method=sign_method, chain_id=chain_id)
        self.quicksigned_tx = quicksigned_tx
    
    def get_signed_cmd(self):
        return self.quicksigned_tx

    def get_cmd_w_sigs(self): 
        cmd_dict = json.loads(self.quicksigned_tx)

        cmd = {
            "cmd": cmd_dict[0]["commandSigData"]["cmd"],
            "sigs": cmd_dict[0]["commandSigData"]["sigs"],
            "hash": cmd_dict[0]["outcome"]["hash"],
        }

        return cmd
