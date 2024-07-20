# Welcome to kad_py!

This library is intended to provide signing and sending pact commands on the Kadena blockchain

## Setup

### Install Pact CLI + Library
TODO 
---------
You will be required to configure the utility to use your desired wallets for the signing and sending to be successful.  

Follow the below steps to complete the configuration:

* Install Pact CLI at [Pact CLI](`https://github.com/kadena-io/pact?tab=readme-ov-file#installing-pact`)
* Create a .env file in the root folder of your project
* Add 3 variables to your .env file: the **PUBLIC_KEY**, **PRIVATE_KEY** , and **DEFAULT_SENDER** values
`PUBLIC_KEY = <your-public-kda-key>`  
`PRIVATE_KEY = <your-secret-kda-key>`
`DEFAULT_SENDER = <your-k-wallet-address>`
* Create a ***keyset.yaml*** file in the ***config*** folder. 
* Add your public KDA key after **public:** as shown  
`public: <your-public-kda-key>`
* Add your secret key after **secret:** as shown  
`secret: <your-secret-kda-key>`


## Functions 

* `execute_exec_cmd` : Takes in a list of params to construct an exec command, then signs (Using pact-cli) it and sends it. 
* `execute_cont_cmd` : Takes in a list of params to construct a cont command, then signs (Using pact-cli) it and sends it.
* `build_exec_cmd` : Takes in a list of params to construct an exec command, returns the raw exec command.
* `build_cont_cmd` : Takes in a list of params to construct a cont command, returns the raw cont command.
* `pact_build_and_fetch_local` : Takes in a list of params to construct an exec command, then sends it via a local call.
* `sign_cmd` : Takes in a raw exec command, signs it via pact CLI and returns it.  
* `quicksign_cmds` : Takes in a list of raw commands, signs it via pact quick sign CLI and returns it.  
* `send_signed` : Takes a signed command and sends it via send signed to pact signing server.
* `pact_fetch_local` : Takes in an exec command, then sends it via a local pact call.


## Example Usage
[link to Example Usages](./example.py)  
Any quick example of import + using our methods