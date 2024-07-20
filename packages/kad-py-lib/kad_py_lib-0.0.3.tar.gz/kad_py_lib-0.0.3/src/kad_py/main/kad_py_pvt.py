""" Module to provide hashing functionality """
import json
import hashlib
import requests

import numpy
from kad_py.utils.io_utils import file_exists, yaml_load, yaml_dump
from kad_py.pact_utils import encoding
from kad_py.commands.command import Command
from kad_py.config.setup import BASE_URL, DEFAULT_NETWORK_ID, DEFAULT_CHAIN_ID, \
    PATH_TO_KEY_YAML, PUBLIC_KEY, PRIVATE_KEY
from kad_py.config.constants import TESTNET_NETWORK_ID, TESTNET_CHAINWEB_URL_PREFIX, \
    MAINNET_CHAINWEB_URL_PREFIX

def hash_command(cmd: object):
    """
    This function creates the hash of the pact command and encodes it to base 64
    """
    command = json.dumps(cmd).encode("utf-8")
    hashinput = hashlib.blake2b(command, digest_size=32)
    hash_digest = hashinput.digest()
    hash_uint8_array = numpy.frombuffer(hash_digest, numpy.uint8)
    
    uintstr = encoding.encoding.uint8ArrayToStr(hash_uint8_array)

    # output1 = encoding.b64url.encode("_ÁÐ'Á7µüè¹ÀµáK¢öPÌô×~$")
    output = encoding.encoding.b64url.encode(uintstr)
    
    # js2py.translate_file("EncodingUtils.js", "encoding.py")

    return output

def build_pact_request_uri(base_url=BASE_URL, network_id=DEFAULT_NETWORK_ID, chain_id=DEFAULT_CHAIN_ID):
    """
    This function builds the URI needed to query the Pact API
    Args:
        base_url (str): the prefix for the url
        network_id (str): specify mainnet or testnet
        chain_id (str): id of chain where called function lives
    
        Returns:
            str: pact request URI
    """

    uri = base_url + network_id + "/chain/" + chain_id + "/pact/api/v1/"

    return uri

def get_url_prefix(network_id:str):
    """
    This function builds the URI needed to query the Pact API
    Args:
        network_id (str): specify mainnet or testnet
    
        Returns:
            str: chainweb URL prefix
    """

    if network_id is TESTNET_NETWORK_ID:
        return TESTNET_CHAINWEB_URL_PREFIX
    return MAINNET_CHAINWEB_URL_PREFIX

def get_api_url(network_id:str, chain_id:str, endpoint:str):
    """
    This function builds the URI needed to query the Pact API
    Args:
        network_id (str): specify mainnet or testnet
        chain_id (str): id of chain where called function lives
        endpoint (str): name of the endpoint called on the Pact API
    
        Returns:
            str: pact request URL
    """

    url = get_url_prefix(network_id=network_id)
    url += network_id + "/chain/" + chain_id + "/pact/api/v1/" + endpoint

    return url

def execute_network_request(url, data, headers, timeout=None):
    """
    This function is a utility to execute an http request and returns the result

    Returns:
        object: deserialized json formatted string into a json object
    """
    try:
        res = requests.post(
            url=url,
            data=data,
            headers=headers,
            timeout=timeout
        )
        if res.status_code == 200:
            return json.loads(res.content.decode("utf-8"))
        elif res.status_code == 400:
            raise requests.exceptions.RequestException
    except requests.exceptions.RequestException as e:
        print(e)
        return None

def get_public_key_from_account(account):
    """
    This function is a utility to return the public key from a given account key

    Returns:
        string: the public key
    """
    return account.split(":")[1]

def set_up_keyset_yaml():
    if PUBLIC_KEY == "" or PUBLIC_KEY == None or PRIVATE_KEY == "" or PRIVATE_KEY == None:
        raise Exception("public and/or private keys are invalid")
    
    keyset = {
        "public": PUBLIC_KEY,
        "secret": PRIVATE_KEY
    }

    if file_exists(PATH_TO_KEY_YAML):
        data = yaml_load(PATH_TO_KEY_YAML)
        if data["public"] is PUBLIC_KEY and data["private"] is PRIVATE_KEY:
            return
    
    yaml_dump(keyset, PATH_TO_KEY_YAML)