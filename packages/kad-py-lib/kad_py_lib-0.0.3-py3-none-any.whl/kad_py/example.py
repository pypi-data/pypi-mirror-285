"""
Module to test this library
"""

from kad_py.config.constants import MAINNET_NETWORK_ID, DEFAULT_GAS_LIMIT, DEFAULT_GAS_PRICE, CLI
import kad_py.main.kad_py_public
import kad_py.commands.env_data
import kad_py.commands.signer

chain_id = "8"

def read_data_from_blockchain(sender, key):
    """
    This function tests fetching local data from the blockchain
    """
    # this is the function from the contract you will be calling
    pact_code = "(free.test-libs.read-data \"" + key + "\")"
    response = kad_py.main.kad_py_public.pact_build_and_fetch_local(sender=sender, pact_code=pact_code, \
        network_id=MAINNET_NETWORK_ID, chain_id=chain_id)

    print(response)

def write_data_from_blockchain(sender, key, value):
    """
    This function tests exec command functionality to write data to the blockchain
    """
    pact_code = "(free.test-libs.write-data \"" + key + "\" \"" + value + "\")"
    env_data = kad_py.commands.env_data.EnvData({})
    response = kad_py.main.kad_py_public.execute_exec_cmd(
        sender=sender,
        code=pact_code,
        chain_id=chain_id,
        gas_price=DEFAULT_GAS_PRICE,
        gas_limit=DEFAULT_GAS_LIMIT,
        signers=[sender],
        env_data=env_data,
        caps=[],
        ttl=600,
        network_id=MAINNET_NETWORK_ID,
        nonce="1234",
        sign_method=CLI
    )

    print(response)

def test_cont_transaction(sender, key, value):
    """
    This function tests the signing and execution of cont commands via a 
    defpact function in the test contract free.test-libs
    """
    pact_code = "(free.test-libs.multi-step-test \"" + key + "\" \"" + value + "\" 2)"
    env_data = kad_py.commands.env_data.EnvData({})
    exec_response = kad_py.main.kad_py_public.execute_exec_cmd(
        sender=sender,
        code=pact_code,
        chain_id=chain_id,
        gas_price=DEFAULT_GAS_PRICE * 2,
        gas_limit=DEFAULT_GAS_LIMIT,
        signers=[sender],
        env_data=env_data,
        caps=[],
        ttl=600,
        network_id=MAINNET_NETWORK_ID,
        nonce="1234",
        sign_method=CLI
    )
    print("--------------------------------------------")
    print("exec response")
    print(exec_response)
    print("--------------------------------------------")

    if "requestKeys" in exec_response:
        cont_response = kad_py.main.kad_py_public.execute_cont_cmd(
            sender=sender,
            chain_id=chain_id,
            gas_price=DEFAULT_GAS_PRICE,
            gas_limit=DEFAULT_GAS_LIMIT,
            ttl=600,
            network_id=MAINNET_NETWORK_ID,
            step=1,
            rollback=False,
            env_data=kad_py.commands.env_data.EnvData({}),
            pact_tx_hash=exec_response["requestKeys"][0],
            sign_method=CLI,
            signers=[sender],
            proof=None
        )

        print("--------------------------------------------")
        print("cont response")
        print(cont_response)
    else:
        print("something went wrong")
        print(cont_response)


read_data_from_blockchain("k:b9b798dd046eccd4d2c42c18445859c62c199a8d673b8c1bf7afcfca6a6a81e3", "someKeys")
# write_data_from_blockchain("k:b9b798dd046eccd4d2c42c18445859c62c199a8d673b8c1bf7afcfca6a6a81e3", "testing", "testing")