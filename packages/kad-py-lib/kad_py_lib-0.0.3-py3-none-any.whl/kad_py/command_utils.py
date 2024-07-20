import os 
import yaml
import subprocess
import sys
import requests
import hashlib
import js2py
sys.path.insert(0, '/Users/mohannadahmad/Desktop/AppDev/Kadena/kadcars_backend_api/kadcarsnft_api/NFTFusion')
from pact_utils.encoding import *
import numpy
import time
from kad_py.config.constants import *

# adding Folder_2 to the system path
sys.path.insert(0, '/Users/mohannadahmad/Desktop/AppDev/Kadena/kadcars_backend_api/kadcarsnft_api/NFTFusion')
from utils.io_utils import *

dirname = os.path.dirname(__file__)
path_to_transforms_folder = os.path.join(dirname, 'metadata_json')
r2r_account  = "k:b9b798dd046eccd4d2c42c18445859c62c199a8d673b8c1bf7afcfca6a6a81e3"
r2r_public_key = "b9b798dd046eccd4d2c42c18445859c62c199a8d673b8c1bf7afcfca6a6a81e3"

def sign_using_pact_cli(transforms, pact_id):
    print(transforms)
    data = {
        "pactTxHash": pact_id,
        "step": 1,
        "rollback": False,
        "data": transforms,
        "networkId": "testnet04",
        "signers": [{"public":r2r_public_key}],
        "publicMeta": {
            "chainId": "1", 
            "sender": r2r_account, 
            "gasLimit": 150000, 
            "gasPrice": 0.00000001, 
            "ttl": 600
        },
        "type": "cont"
    }

    #prepare unsigned transaction data
    path_to_tx_yaml = "tx.yaml"
    path_to_r2r_key_yaml = "keyset.yaml"
    path_to_tx_signed_yaml = "tx-signed.yaml"
    path_to_tx_unsigned_yaml = "tx-unsigned.yaml"

    #create tx file with above data
    with open(path_to_tx_yaml, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    #Convert the transaction to an unsigned prepared form that signatures can be added to
    subprocess.run("pact -u " + path_to_tx_yaml + " > " + path_to_tx_unsigned_yaml, shell=True)
    
    #sign the prepared transaction
    subprocess.run("cat " + path_to_tx_unsigned_yaml + " | " + "pact add-sig " + path_to_r2r_key_yaml + " > " + path_to_tx_signed_yaml, shell=True)

def send_transaction():
    command = ""
    
    with open("tx-signed.yaml", 'r') as f:
        command = f.read()
    f.close()

    print(command)

    headers = {
        "Content-Type": "application/json"
    }
    command = json.loads(command,)
    print(command)
    response = requests.post("https://api.testnet.chainweb.com/chainweb/0.0/testnet04/chain/1/pact/api/v1/send", headers=headers, json=command)
    print(response.text)

def pact_fetch_local(pact_code, network_id, chain_id):
    cmd_string = assemble_command_for_pact_api(pact_code=pact_code, chain_id=chain_id)
    hash_string = hash_command(cmd_string)

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "hash": hash_string,
        "sigs": [],
        "cmd": cmd_string
    }

    try:
        response = requests.post(pact_fetch_local_url_prefix + network_id + "/chain/" + chain_id + "/pact/api/v1/local", json=payload, headers=headers)
        print(response.json())

        return response.json()
    except Exception as e:
        print(e)

def hash_command(input):
    hashinput = hashlib.blake2b(input.encode("utf-8"), digest_size=32)
    hash_digest = hashinput.digest()
    hash_uint8_array = numpy.frombuffer(hash_digest, numpy.uint8)
    
    uintstr = encoding.uint8ArrayToStr(hash_uint8_array)

    # output1 = encoding.b64url.encode("_ÁÐ'Á7µüè¹ÀµáK¢öPÌô×~$")
    output = encoding.b64url.encode(uintstr)
    
    # js2py.translate_file("EncodingUtils.js", "encoding.py")

    return output

#API
def assemble_command_for_pact_api(pact_code, chain_id, data={}):
    command = {
        "meta": {
            "chainId": chain_id,
            "creationTime": round(time.time(), 2),
            "gasLimit": 150000,
            "gasPrice": 3e-8,
            "sender": r2r_account,
            "ttl": 7200 #TODO: change back to 600
        },
        # "networkId": "testnet04",
        "networkId": "mainnet01",
        "nonce": "123",
        "payload": {
            "exec": {
                "code": pact_code,
                "data": data
            }
        },
        "signers": []
    }

    return json.dumps(command)