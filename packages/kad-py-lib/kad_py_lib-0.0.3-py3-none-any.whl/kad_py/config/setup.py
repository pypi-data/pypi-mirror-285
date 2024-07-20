import os
from dotenv import load_dotenv

env = load_dotenv(verbose=True, override=True)
dirname = os.path.dirname(__file__)

PUBLIC_KEY = os.getenv("PUBLIC_KEY")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

BASE_URL = "https://api.chainweb.com/chainweb/0.0/"
MAINNET_NETWORK_ID = "mainnet01"
TESTNET_NETWORK_ID = "testnet04"
NETWORK_ID = MAINNET_NETWORK_ID

DEFAULT_WALLET_TYPE = "chainweaver"

DEFAULT_SENDER = os.getenv("DEFAULT_SENDER")
DEFAULT_CHAIN_ID = "8"
DEFAULT_GAS_PRICE = 1e-8
DEFAULT_GAS_LIMIT = 150000
DEFAULT_TTL = 600
DEFAULT_NONCE = ""

TESTNET_NETWORK_ID = "testnet04"
MAINNET_NETWORK_ID = "mainnet01"
DEFAULT_NETWORK_ID = MAINNET_NETWORK_ID

PATH_TO_TX_YAML = dirname + "/../yaml_files/tx.yaml"
PATH_TO_KEY_YAML = dirname + "/keyset.yaml"
PATH_TO_TX_SIGNED_YAML = dirname + "/../yaml_files/tx-signed.yaml"
PATH_TO_TX_UNSIGNED_YAML = dirname + "/../yaml_files/tx-unsigned.yaml"

DEFAULT_REQUEST_HEADERS = {
    "Content-Type": "application/json"
}

WALLET_HOST_BASE_URL = "http://localhost:9467"