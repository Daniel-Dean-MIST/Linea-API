from flask import Flask, request, jsonify
from web3 import Web3

import json

def get_transaction_data():
    # Fetch transaction data from the blockchain or any relevant source
    transaction_data = {
        "txHash": "0x1234567890abcdef1234567890abcdef1234567890",
        "timestamp": 1671436800,  # Replace with actual UTC timestamp
        "tokenAddress": "0x176211869ca2b568f2a7d4ee941e073a821ee1ff",
        "tokenVolume": "10000000",
        "tokenUSDAmount": 10.01,
        "lendBorrowType": "BORROW"  # Replace with actual lend/borrow type
    }

    return transaction_data

def prepare_api_response(data):
    if data is None:
        error_response = {
            "error": {
                "code": 1,
                "message": "No transaction data found"
            }
        }
        return json.dumps(error_response)

    result = [{
        "txHash": data["txHash"],
        "timestamp": data["timestamp"],
        "tokenAddress": data["tokenAddress"],
        "tokenVolume": data["tokenVolume"],
        "tokenUSDAmount": data["tokenUSDAmount"],
        "lendBorrowType": data["lendBorrowType"]
    }]

    response = {
        "error": {
            "code": 0,
            "message": "Success"
        },
        "data": {
            "result": result
        }
    }

    return json.dumps(response)

def main():
    transaction_data = get_transaction_data()
    api_response = prepare_api_response(transaction_data)
    print(api_response)  # This will print the formatted JSON response

if __name__ == "__main__":
    main()