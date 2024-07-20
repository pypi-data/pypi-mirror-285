"""
This module contains the functions to sign exec or cont commands to 
be executed and sent on the kadena blockchain either with the CLI
or the Pact server API
"""
import requests
import subprocess

from kad_py.commands.command import Command
from kad_py.utils.io_utils import yaml_dump, yaml_load
from kad_py.main.kad_py_pvt import execute_network_request, set_up_keyset_yaml
from kad_py.config.setup import WALLET_HOST_BASE_URL, DEFAULT_REQUEST_HEADERS, \
    PATH_TO_TX_YAML, PATH_TO_TX_SIGNED_YAML, PATH_TO_TX_UNSIGNED_YAML, \
    PATH_TO_KEY_YAML

def sign_w_api(cmd: Command):
    """
    This function signs a given exec or cont command using the Pact API

    Returns:
        object: the result of the signed transaction
    """
    signable_cmd = cmd.get_cmd()["cmd"]

    try:
        response = execute_network_request(WALLET_HOST_BASE_URL + "/v1/sign", signable_cmd, DEFAULT_REQUEST_HEADERS)
        return response
    except requests.exceptions.RequestException as e:
        print(e)
        return e

def quicksign_w_api(cmds: list[Command]):
    """
    This function signs the given commands using the quicksign API

    Returns:
        object: the result of the quicksigned transaction
    """
    try:
        pass
    except requests.exceptions.RequestException as e:
        print(e)
        return e

def sign_w_cli(cmd: Command):
    """
    This function signs a given exec or cont command using the Pact CLI

    Returns:
        object: the result of the signed transaction
    """
    yaml_file_paths = [PATH_TO_TX_YAML, PATH_TO_TX_UNSIGNED_YAML, PATH_TO_TX_SIGNED_YAML]
    try:
        for file_path in yaml_file_paths:
            with open(file_path, 'w') as initial_file_create: 
                pass
            initial_file_create.close()
    except Exception as e:
        print(e)

    set_up_keyset_yaml()

    signable_cmd = cmd.get_cmd()["cmd"]

    yaml_dump_success = yaml_dump(signable_cmd, PATH_TO_TX_YAML)
    assert(yaml_dump_success is True), "Dumping command to yaml failed"

    #Convert the transaction to an unsigned prepared form that signatures can be added to
    try:
        #Convert the transaction to an unsigned prepared form that signatures can be added to
        subprocess.run(
            "pact -u " + PATH_TO_TX_YAML + " > " + PATH_TO_TX_UNSIGNED_YAML, \
                shell=True, check=False)

        #sign the prepared transaction
        subprocess.run(
            "cat " + PATH_TO_TX_UNSIGNED_YAML + " | " + "pact add-sig " + \
                PATH_TO_KEY_YAML + " > " + PATH_TO_TX_SIGNED_YAML, shell=True, check=False)
    except Exception as e:
        print(e)
        return None
    
    signed_tx = yaml_load(PATH_TO_TX_SIGNED_YAML)
    assert(signed_tx is not None), "Loading signed transaction from yaml file failed"

    return signed_tx