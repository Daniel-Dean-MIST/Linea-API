from flask import Flask, request, jsonify
from web3 import Web3

app = Flask(__name__)

# Replace with the actual Optimism RPC URL
optimism_rpc_url = "https://mainnet-optimism.infura.io/v3/YOUR_INFURA_PROJECT_ID"

# Create a Web3 instance to connect to the Optimism blockchain
web3 = Web3(Web3.HTTPProvider(optimism_rpc_url))

# Define the contract address
contract_address = "0xfF94cc8E2c4B17e3CC65d7B83c7e8c643030D936"

@app.route("/balanceOf/<address>", methods=["GET"])
def balance_of(address):
    # Get the contract instance
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    # Call the balanceOf function to get the account balance
    balance = contract.functions.balanceOf(address).call()

    # Return the balance in JSON format
    return jsonify({"balance": balance})

if __name__ == "__main__":
    app.run(debug=True)
