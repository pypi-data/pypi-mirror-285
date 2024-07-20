import os 
import yaml
import subprocess
import sys
sys.path.insert(0, '/Users/mohannadahmad/Desktop/AppDev/Kadena/kadcars_backend_api/kadcarsnft_api/NFTFusion')
import requests
import hashlib
from pact_utils.encoding import *
import numpy
from kad_py.config.constants import pact_fetch_local_url_prefix, testnet_network_id, default_chain_id
from command_utils import *

# adding Folder_2 to the system path
from utils.io_utils import *

dirname = os.path.dirname(__file__)
path_to_transforms_folder = os.path.join(dirname, 'metadata_json')
r2r_public_account = "k:b9b798dd046eccd4d2c42c18445859c62c199a8d673b8c1bf7afcfca6a6a81e3"
r2r_public_key = "b9b798dd046eccd4d2c42c18445859c62c199a8d673b8c1bf7afcfca6a6a81e3"
ipfs_gateway = "ipfs.io"

def sign_using_pact_cli(transforms, pact_id):
    print(transforms)
    data = {
        "pactTxHash": "6Te22fUzf-9ynFfzYTYnKLzVVU2JhqhimJPgYGyuAwQ",
        "step": 1,
        "rollback": False,
        "data": transforms,
        "networkId": "testnet04",
        "signers": [{"public":r2r_public_key}],
        "publicMeta": {
            "chainId": "1", 
            "sender": r2r_public_account, 
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


def download_webp_assets(manifest):
    response = ""
    try:
        #download WEBP
        response = requests.get("https://" + manifest["uri"]["data"].split("//")[1] + ".ipfs.nftstorage.link?download=true", allow_redirects=True)
        
        if response.status_code == 200:
            write_asset_data_to_file('asset_render.webp', response.content)

    except:
        print()
        print("Failed to fetch asset from IPFS")


def download_glb_asset(manifest):
    glb_ipfs_dir_cid = manifest["data"][2]["datum"]["art-asset"]["data"].split("//")[1]
    glb_ipfs_asset_file_name = ""
    glb_ipfs_asset_cid = ""

    try:
        response = requests.get("https://" + ipfs_gateway + "/api/v0/ls?arg=" + glb_ipfs_dir_cid)
        
        if response.status_code == 200:
            glb_ipfs_asset_cid = response.json()["Objects"][0]["Links"][0]["Hash"]
            glb_ipfs_asset_file_name = response.json()["Objects"][0]["Links"][0]["Name"]

            print("https://" + glb_ipfs_dir_cid + ".ipfs.nftstorage.link/ipfs/" + glb_ipfs_asset_cid + "?filename=" + glb_ipfs_asset_file_name)
            
            try:
                res = requests.get("https://" + glb_ipfs_dir_cid + ".ipfs.nftstorage.link/ipfs/" + glb_ipfs_asset_cid + "?filename=" + glb_ipfs_asset_file_name, allow_redirects=True)

                if res.status_code == 200:
                    write_asset_data_to_file('asset_glb.glb', res.content)
            except:
                print("Error downloading GLB")
    except:
        print("Failed to retrieve GLB ipfs directory data")

def write_asset_data_to_file(filename, data):
    try:
        with open(filename, 'wb') as f:
            f.write(data)
        f.close()

        return True
    except:
        print("Error outputting asset file data")

    return False


def hash_command(input):
    hashinput = hashlib.blake2b(input.encode("utf-8"), digest_size=32)
    hash_digest = hashinput.digest()
    hash_uint8_array = numpy.frombuffer(hash_digest, numpy.uint8)
    
    uintstr = encoding.uint8ArrayToStr(hash_uint8_array)

    # output1 = encoding.b64url.encode("_ÁÐ'Á7µüè¹ÀµáK¢öPÌô×~$")
    output = encoding.b64url.encode(uintstr)
    # print(output)

    return output

def get_new_datum(datum, uri):
    pact_code = "(kip.token-manifest.create-datum " + json.dumps(uri) + " " + json.dumps(datum) + ")"
    cmd_string = assemble_command_for_pact_api(pact_code=pact_code, chain_id=default_chain_id)
    cmd_hash = hash_command(cmd_string)

    payload = {
        "hash": cmd_hash,
        "sigs": [],
        "cmd": cmd_string
    }

    try:
        response = requests.post(pact_fetch_local_url_prefix + testnet_network_id + "/chain/" + default_chain_id + "/pact/api/v1/local", json=payload, headers={"Content-Type":"application/json"})

        if response.status_code == 200:
            return response.json()["result"]["data"]
    except:
        print("Error getting new datum")

def get_nft_from_blockchain():
    # cmd_string = "{\"networkId\":null,\"payload\":{\"exec\":{\"data\":{},\"code\":\"(free.kadcars-ledger-policy.get-minted-tokens-for-collection \\\"k2:final\\\")\"}},\"signers\":[],\"meta\":{\"creationTime\":1678055190,\"ttl\":600,\"gasLimit\":150000,\"chainId\":\"1\",\"gasPrice\":1e-8,\"sender\":\"\"},\"nonce\":\"\\\"2023-03-05T22:26:39.679Z\\\"\"}"
    
    pact_contract = "(free.universal-ledger.get-manifest"

    cmd_string = assemble_command_for_pact_api(pact_contract + " \"" + "Kadcars#K:2 Diamond Back->>>>>>" + "\")", default_chain_id)
    hash_string = hash_command(cmd_string)
    obj = {
        "hash": "OyuhWgZimn81PAL74QR3UAvbu6fFcYlaL-sVr1b0IYM",
        "sigs": [],
        "cmd": "{\"networkId\":null,\"payload\":{\"exec\":{\"data\":{},\"code\":\"(coin.details \\\"k:f157854c15e9bb8fb55aafdecc1ce27a3d60973cbe6870045f4415dc06be06f5\\\")\"}},\"signers\":[],\"meta\":{\"creationTime\":1678340114,\"ttl\":600,\"gasLimit\":150000,\"chainId\":\"1\",\"gasPrice\":1e-8,\"sender\":\"\"},\"nonce\":\"\\\"2023-03-09T05:35:24.242Z\\\"\"}"
    }

    payload = {
        "hash": hash_string,
        "sigs": [],
        "cmd": cmd_string
    }

    try:
        manifest = {}
        # response = requests.post(pact_fetch_local_url_prefix + testnet_network_id + "/chain/" + default_chain_id + "/pact/api/v1/local", json=json.dumps(payload))
        response = requests.post("https://api.testnet.chainweb.com/chainweb/0.0/testnet04/chain/1/pact/api/v1/local", json=payload, headers={"Content-Type":"application/json"})
        # export_dictionary_to_json(response.json(), "test.json")
        # print(response.json()["result"]["data"]["data"])

        if response.status_code == 200:
            file_read = extract_data_from_json("test.json.json")
            print(file_read)
            manifest = response.json()["result"]["data"]
            manifest_data = manifest["data"]
            
            for datum in manifest_data:
                if datum["uri"]["data"] == "nft-references":
                    new_sticker = {
                        "sticker": "sticker_id"
                    }
                    datum["uri"]["data"]["datum"]["stickers"].append(new_sticker)

                    new_datum = datum["uri"]["data"]["datum"]
                    new_uri = datum["uri"]["data"]["uri"]

                    hashed_datum = get_new_datum(datum=new_datum, uri=new_uri)

                    datum = hashed_datum

                    export_dictionary_to_json(manifest, "test")

            new_datum = {
                "art-asset": {
                    "data": "ipfs://bafybeiezex5grbqllavehqg4l5yry6eyd6whfsavng3wahguio5l4kaiba",
                    "scheme": "ipfs://"
                }
            }

            uri = {
                "data": "nft-references",
                "scheme": "pact:schema"
            }

            create_datum_contract_res = get_new_datum(datum=new_datum, uri=uri)
            
            manifest_data.append(create_datum_contract_res)

            print(manifest_data)

            export_dictionary_to_json(manifest_data, "test")

        return manifest
        
    except Exception as e:
        print(e)
        print("Error with post request")

# manifest = extract_data_from_json("test_manifest.json")
# download_glb_asset(manifest)

# input = "{\"networkId\":\"testnet04\",\"payload\":{\"cont\":{\"proof\":null,\"data\":{\"kc\":{\"pred\":\"keys-all\",\"keys\":[\"f157854c15e9bb8fb55aafdecc1ce27a3d60973cbe6870045f4415dc06be06f5\"]},\"transformation-list\":[{\"transform\":{\"obj\":{\"uri\":{\"data\":\"view-references\",\"scheme\":\"ipfs\"},\"new-datum\":{\"hash\":\"6Te22fUzf-9ynFfzYTYnKLzVVU2JhqhimJPgYGyuAwQ\",\"uri\":{\"data\":\"view-references\",\"scheme\":\"pact:schema\"},\"datum\":{\"art-asset\":{\"data\":\"ipfs://bafybeielzyapofnglxicaith7etxczpxq3psaeq6uh7chuh6dtbbmtqyny\",\"scheme\":\"ipfs://\"}}}},\"type\":\"replace\"}},{\"transform\":{\"obj\":{\"hash\":\"6Te22fUzf-9ynFfzYTYnKLzVVU2JhqhimJPgYGyuAwQ\",\"uri\":{\"data\":\"nft-references\",\"scheme\":\"pact:schema\"},\"datum\":{\"test\":\"test\"}},\"type\":\"add\"}},{\"transform\":{\"obj\":{\"uri\":{\"data\":\"ipfs://bafybeia3obqfvgnxpm56oan2b7mempewuml4xynlcgkodks6tf44b3hnie\",\"scheme\":\"ipfs\"}},\"type\":\"uri\"}}]},\"pactId\":\"DycORcKohpEWlyC6VxX9pcT28y_bP-G52xjlGqAaUVc\",\"rollback\":false,\"step\":2}},\"signers\":[{\"pubKey\":\"b9b798dd046eccd4d2c42c18445859c62c199a8d673b8c1bf7afcfca6a6a81e3\"}],\"meta\":{\"creationTime\":1678004406,\"ttl\":6000,\"gasLimit\":150000,\"chainId\":\"1\",\"gasPrice\":1.0e-8,\"sender\":\"k:b9b798dd046eccd4d2c42c18445859c62c199a8d673b8c1bf7afcfca6a6a81e3\"},\"nonce\":\"\\\"2023-03-05 08:20:06.599883 UTC\\\"\"}"
# output = hashCommand(input)

# transform_data = extract_data_from_json('transforms.json')[0]["transform"]["obj"]["new-datum"]["datum"]
# hash_command(json.dumps(transform_data))
# sign_using_pact_cli(transform_data, "6Te22fUzf-9ynFfzYTYnKLzVVU2JhqhimJPgYGyuAwQ")
# send_transaction()

datum = {
    "test":"",
    "id":"",
    "nft-ref":[]
}
uri = {
    "data":"",
    "scheme":""
}



# get_new_datum(datum=datum, uri=uri)

# get_nft_from_blockchain()