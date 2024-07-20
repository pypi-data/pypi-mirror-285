"""
This module provides users with ability to build, 
sign and send exec and cont transactions with Pact CLI and API
"""

import json

from kad_py.commands.capability import Capability
from kad_py.commands.env_data import EnvData
from kad_py.commands.command import Command
from kad_py.commands.command_metadata import CommandMetadata
from kad_py.commands.signer import Signer
from kad_py.commands.exec_command import ExecCommand
from kad_py.commands.cont_command import ContCommand
from kad_py.transactions.transaction import Transaction
from kad_py.transactions.pact_sign_transaction import PactSignTransaction
from kad_py.transactions.quicksign_transaction import QuickSignTransaction
from kad_py.config.setup import DEFAULT_WALLET_TYPE, DEFAULT_REQUEST_HEADERS, DEFAULT_NETWORK_ID
from kad_py.config.constants import API, CLI, SEND, LOCAL
from kad_py.sign.sign import sign_w_cli, sign_w_api, quicksign_w_api
from kad_py.main import kad_py_pvt

def execute_exec_cmd(
    sender: str,
    code: str,
    chain_id: str,
    gas_price: int,
    gas_limit: int,
    signers: list[Signer], #TODO: fix signers
    env_data: EnvData,
    caps: list[Capability],
    ttl: int,
    nonce: str,
    network_id: str,
    sign_method: str
):
    """
    This function builds, signs and sends an exec command 
    
    Args:
        sender (str): address of wallet executing command
        code (str): pact code to be called on the blockchain
        chain_id (str): id of the chain where code contract lives
        gas_price (int): gas to be spent on transaction
        gas_limit (int): upper limit of gas cost for transaction
        signers (list[str]): addresses of wallets signing transaction
        env_data (EnvData): additional data sent needed by blockchain function
        caps (list[Capability]): capabilities needed for transaction to execute successfully
        ttl (int): time limit before transaction times out
        nonce (str): nonce
        network_id (str): specifies mainnet or testnet
    
    Returns:
        Object: response from sending signed command over Pact API 
    """

    exec_cmd = build_exec_cmd(
        sender=sender,
        code=code,
        chain_id=chain_id,
        gas_price=gas_price,
        gas_limit=gas_limit,
        signers=signers,
        env_data=env_data,
        caps=caps,
        ttl=ttl,
        network_id=network_id,
        nonce=nonce
    )

    signed_transaction = sign_cmd(exec_cmd, sign_method)

    tx_response = send_signed(signed_transaction)

    return tx_response

def execute_cont_cmd(
    sender: str,
    chain_id: str,
    gas_price: int,
    gas_limit: int,
    ttl: int,
    network_id: str,
    step: int,
    rollback: bool,
    env_data: EnvData,
    pact_tx_hash: str,
    sign_method: str,
    signers: list[str],
    caps: list[Capability],
    proof: str
):
    """
    This function builds, signs and sends a cont command , a step in a defpact
    
    Args:
        sender (str): address of wallet executing command
        chain_id (str): id of the chain where code contract lies
        gas_price (int): gas to be spent on transaction
        gas_limit (int): upper limit of gas cost for transaction
        ttl (int): time limit before transaction times out
        network_id (str): specifies mainnet or testnet
        step (int): number of step in defpact
        rollback (bool): indicates whether transaction can be rolled back
        env_data (EnvData): additional data sent needed by blockchain function
        pact_tx_hash (str): hash for defpact to continue
    
    Returns:
        Object: response from sending signed command over Pact API 
    """

    cont_cmd = build_cont_cmd(
        sender=sender,
        chain_id=chain_id,
        gas_limit=gas_limit,
        gas_price=gas_price,
        ttl=ttl,
        network_id=network_id,
        step=step,
        rollback=rollback,
        env_data=env_data,
        pact_tx_hash=pact_tx_hash,
        signers=signers,
        caps=caps,
        proof=proof
    )

    signed_transaction = sign_cmd(cont_cmd, sign_method)
    tx_response = send_signed(signed_transaction)

    return tx_response

def build_exec_cmd(
    sender: str,
    code: str,
    chain_id: str,
    gas_price: int,
    gas_limit: int,
    signers: list[str],
    env_data: EnvData,
    caps: list[Capability],
    ttl: int,
    nonce: str,
    network_id: str
):
    """
    This function builds an exec command 
    
    Args:
        sender (str): address of wallet executing command
        code (str): pact code to be called on the blockchain
        chain_id (str): id of the chain where code contract lies
        gas_price (int): gas to be spent on transaction
        gas_limit (int): upper limit of gas cost for transaction
        signers (list[str]): addresses of wallets signing transaction
        env_data (EnvData): additional data sent needed by blockchain function
        caps (list[Capability]): capabilities needed for transaction to execute successfully
        ttl (int): time limit before transaction times out
        nonce (str): nonce
        network_id (str): specifies mainnet or testnet
    
    Returns:
        ExecCommand: object of type Command containing cmd ready for signing and sending
    """

    exec_cmd = ExecCommand(
        sender=sender,
        code=code,
        chain_id=chain_id,
        gas_price=gas_price,
        gas_limit=gas_limit,
        signers=signers,
        data=env_data,
        caps=caps,
        ttl=ttl,
        network_id=network_id,
        nonce=nonce
    )

    return exec_cmd

def build_cont_cmd(
        sender: str,
        chain_id: str,
        gas_price: int,
        gas_limit: int,
        ttl: int,
        network_id: str,
        step: int,
        rollback: bool,
        env_data: EnvData,
        pact_tx_hash: str,
        signers: list[str],
        caps: list[Capability],
        proof: str
):
    """
    This function builds a cont command 
    
    Args:
        sender (str): address of wallet executing command
        chain_id (str): id of the chain where code contract lies
        gas_price (int): gas to be spent on transaction
        gas_limit (int): upper limit of gas cost for transaction
        ttl (int): time limit before transaction times out
        network_id (str): specifies mainnet or testnet
        step (int): number of step in defpact
        rollback (bool): indicates whether transaction can be rolled back
        env_data (EnvData): additional data sent needed by blockchain function
        pact_tx_hash (str): hash for defpact to continue
    
    Returns:
        ContCommand: object of type Command containing cmd ready for signing and sending
    """

    cont_cmd = ContCommand(
        sender=sender,
        chain_id=chain_id,
        gas_limit=gas_limit,
        gas_price=gas_price,
        ttl=ttl,
        network_id=network_id,
        step=step,
        rollback=rollback,
        data=env_data,
        pact_tx_hash=pact_tx_hash,
        signers=signers,
        caps=caps,
        proof=proof
    )

    return cont_cmd

def quicksign_and_send_cmds(cmds: list[Command], sign_method: str):
    """
    This function calls the quicksign API to sign transactions part of defpact
    or a group of transactions simultaneously

    Args:
        cmds (list[Command]): commands to be signed and sent
    
    Returns:
        Blockchain send response 
    """
    quicksigned_tx = quicksign_cmds(cmds, sign_method)
    quicksigned_tx_to_send = quicksigned_tx.get_cmd_w_sigs()
    
    network_url = kad_py_pvt.build_pact_request_uri()
    response = kad_py_pvt.execute_network_request(network_url, json.dumps(quicksigned_tx_to_send), DEFAULT_REQUEST_HEADERS)

    return response

def quicksign_cmds(
    cmds: list[Command], 
    sign_method:str, 
    chain_id:str, 
    wallet_type=DEFAULT_WALLET_TYPE, 
    network_id=DEFAULT_NETWORK_ID
):
    """
    This function calls the quicksign API to sign transactions part of defpact
    or a group of transactions simultaneously

    Args:
        cmds (list[Command]): commands to be signed by quicksign API
    
    Returns:
        QuickSignTransaction: commands quicksigned via quicksign API
    """

    cmds = [cmd.get_cmd_for_api() for cmd in cmds]
    
    quicksigned_tx = None
    cmd_to_quicksign = {}
    if wallet_type is DEFAULT_WALLET_TYPE:
        cmd_to_quicksign["cmdSigDatas"] = []
    
    for cmd in cmds:
        cmd_obj = {
            "sigs": cmd["sigs"],
            "cmd": cmd["cmd"]
        }
        cmd_to_quicksign["cmdSigDatas"].append(cmd_obj)

    quicksigned_tx = None
    if sign_method == CLI:    
        quicksigned_tx = sign_w_cli(cmds[0]["cmd"])
    elif sign_method == API:
        quicksigned_tx = quicksign_w_api(cmds[0]["cmd"])


    quicksign_transaction = QuickSignTransaction(quicksigned_tx, network_id, sign_method, chain_id)
    
    return quicksign_transaction

def sign_cmd(cmd: Command, sign_method: str = CLI):
    """
    This function signs a command of type exec or cont using the pact signing CLI

    Args:
        cmd (Command): command to be signed
    
    Returns:
        PactSignTransaction: object with hash, and signed command
    """
    #Create yaml file with cmd data
    chain_id = cmd.get_cmd_meta().get_cmd_meta()["chainId"]

    signed_tx = None
    if sign_method == CLI:
        signed_tx = sign_w_cli(cmd)
    elif sign_method == API:
        signed_tx = sign_w_api(cmd)

    signed_transaction = PactSignTransaction(signed_tx, cmd.get_network_id(), sign_method, chain_id)

    return signed_transaction

def send_signed(signed_tx: Transaction):
    """
    This functions sends a signed transaction via Pact cLI

    Args:
        signed_tx (Transaction): signed transaction ready for sending

    Returns:
        object: response from Pact API
    """

    network_url = kad_py_pvt.get_api_url(signed_tx.get_network_id(), signed_tx.get_chain_id(), SEND)
    signed_tx_obj = signed_tx.get_signed_cmd()

    response = kad_py_pvt.execute_network_request(network_url, json.dumps(signed_tx_obj), DEFAULT_REQUEST_HEADERS)

    return response

def pact_build_and_fetch_local(sender: str, pact_code: str, network_id: str, chain_id: str):
    """
    This function executes a simple query to fetch data from the blockchain locally without executing a transaction
    Args:
        pact_code (str): code to be called on blockchain
        network_id (str): specify mainnet or testnet
        chain_id (str): id of chain where called function lives
    
    Returns:
        Object: response object from blockchain
    """

    meta = CommandMetadata()
    meta = meta.get_cmd_meta()
    env_data = EnvData({})
    cmd = ExecCommand(
        sender,
        chain_id,
        meta["gasPrice"],
        meta["gasLimit"],
        meta["ttl"],
        network_id,
        pact_code,
        env_data
    )

    payload = cmd.get_cmd_for_api()
    response = pact_fetch_local(payload, network_id, chain_id)
    
    return response

def pact_fetch_local(payload:object, network_id: str, chain_id: str):
    """
    This function calls the Pact API with a given payload
    Args:
        payload (object): the object containing the command, hash and sigs
        network_id (str): the ID of the network used (mainnet01 or testnet04)
        chain_id (str): the ID of the chain to call the contract on

    Returns:
        the reponse from the API endpoint that is called
    """
    headers = {
        "Content-Type": "application/json"
    }

    network_url = kad_py_pvt.get_api_url(network_id=network_id, chain_id=chain_id, endpoint=LOCAL)
    response = kad_py_pvt.execute_network_request(network_url, json.dumps(payload), headers)
    
    return response

def build_cap(role: str, description: str, name:str, args: list):
    """
    This function builds Capability objects for transactions

    Args:
        role (str): role of capability
        description (str): description of capability and its purpose
        name (str): capability name
        args (list): args capability expects as per its contract

    Returns:
        Capability: object encapsulating capability data
    """
    cap =  Capability(role=role, description=description, name=name, args=args)

    return cap
