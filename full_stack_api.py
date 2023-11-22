from flask import Flask, request, jsonify
from web3 import Web3
from web3.middleware import geth_poa_middleware
import pandas as pd
import json
import requests
import threading

app = Flask(__name__)

# Replace with the actual Optimism RPC URL
optimism_rpc_url = "https://linea-mainnet.infura.io/v3/e2b4d9fa19c748489fb6c0d6bf411be4"

# Create a Web3 instance to connect to the Optimism blockchain
web3 = Web3(Web3.HTTPProvider(optimism_rpc_url))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Replace with the actual Aave V2 contract address
# contract_address = "0x871AfF0013bE6218B61b28b274a6F53DB131795F"


#gets how many decimals our reserve is
def get_reserve_decimals(reserve_address):
    decimals = 0
    if reserve_address == '0x4AF15ec2A0BD43Db75dd04E62FAA3B8EF36b00d5': # dai
        decimals = 1e18
    elif reserve_address == '0x176211869cA2b568f2A7D4EE941E073a821EE1ff': # usdc
        decimals = 1e6
    elif reserve_address == '0xA219439258ca9da29E9Cc4cE5596924745e12B93': # usdt
        decimals = 1e6
    elif reserve_address == '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f': # weth
        decimals = 1e18
    elif reserve_address == '0x3aAB2285ddcDdaD8edf438C1bAB47e1a9D05a9b4': # wbtc
        decimals = 1e8
    
    return decimals
#gets our reserve price
def get_tx_usd_amount(reserve_address, token_amount):
    contract_address = '0x8429d0AFade80498EAdb9919E41437A14d45A00B'
    contract_abi = [{"inputs":[{"internalType":"address[]","name":"assets","type":"address[]"},{"internalType":"address[]","name":"sources","type":"address[]"},{"internalType":"address","name":"fallbackOracle","type":"address"},{"internalType":"address","name":"baseCurrency","type":"address"},{"internalType":"uint256","name":"baseCurrencyUnit","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"asset","type":"address"},{"indexed":True,"internalType":"address","name":"source","type":"address"}],"name":"AssetSourceUpdated","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"baseCurrency","type":"address"},{"indexed":False,"internalType":"uint256","name":"baseCurrencyUnit","type":"uint256"}],"name":"BaseCurrencySet","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"fallbackOracle","type":"address"}],"name":"FallbackOracleUpdated","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":True,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"inputs":[],"name":"BASE_CURRENCY","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"BASE_CURRENCY_UNIT","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getAssetPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address[]","name":"assets","type":"address[]"}],"name":"getAssetsPrices","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getFallbackOracle","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getSourceOfAsset","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[]","name":"assets","type":"address[]"},{"internalType":"address[]","name":"sources","type":"address[]"}],"name":"setAssetSources","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"fallbackOracle","type":"address"}],"name":"setFallbackOracle","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    value_usd = contract.functions.getAssetPrice(reserve_address).call()
    decimals = get_reserve_decimals(reserve_address)
    usd_amount = (value_usd/1e18)*(token_amount/decimals)
    # print(usd_amount)
    return usd_amount

#gets our web3 contract object
def get_contract():
    contract_address = "0x871AfF0013bE6218B61b28b274a6F53DB131795F"
    contract_abi = [{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"reserve","type":"address"},{"indexed":False,"internalType":"address","name":"user","type":"address"},{"indexed":True,"internalType":"address","name":"onBehalfOf","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"borrowRateMode","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"borrowRate","type":"uint256"},{"indexed":True,"internalType":"uint16","name":"referral","type":"uint16"}],"name":"Borrow","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"reserve","type":"address"},{"indexed":False,"internalType":"address","name":"user","type":"address"},{"indexed":True,"internalType":"address","name":"onBehalfOf","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":True,"internalType":"uint16","name":"referral","type":"uint16"}],"name":"Deposit","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"target","type":"address"},{"indexed":True,"internalType":"address","name":"initiator","type":"address"},{"indexed":True,"internalType":"address","name":"asset","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"premium","type":"uint256"},{"indexed":False,"internalType":"uint16","name":"referralCode","type":"uint16"}],"name":"FlashLoan","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"collateralAsset","type":"address"},{"indexed":True,"internalType":"address","name":"debtAsset","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"uint256","name":"debtToCover","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"liquidatedCollateralAmount","type":"uint256"},{"indexed":False,"internalType":"address","name":"liquidator","type":"address"},{"indexed":False,"internalType":"bool","name":"receiveAToken","type":"bool"}],"name":"LiquidationCall","type":"event"},{"anonymous":False,"inputs":[],"name":"Paused","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"reserve","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"}],"name":"RebalanceStableBorrowRate","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"reserve","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":True,"internalType":"address","name":"repayer","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Repay","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"reserve","type":"address"},{"indexed":False,"internalType":"uint256","name":"liquidityRate","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"stableBorrowRate","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"variableBorrowRate","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"liquidityIndex","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"variableBorrowIndex","type":"uint256"}],"name":"ReserveDataUpdated","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"reserve","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"}],"name":"ReserveUsedAsCollateralDisabled","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"reserve","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"}],"name":"ReserveUsedAsCollateralEnabled","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"reserve","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"uint256","name":"rateMode","type":"uint256"}],"name":"Swap","type":"event"},{"anonymous":False,"inputs":[],"name":"Unpaused","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"reserve","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Withdraw","type":"event"},{"inputs":[],"name":"FLASHLOAN_PREMIUM_TOTAL","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"LENDINGPOOL_REVISION","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"MAX_NUMBER_RESERVES","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"MAX_STABLE_RATE_BORROW_SIZE_PERCENT","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"interestRateMode","type":"uint256"},{"internalType":"uint16","name":"referralCode","type":"uint16"},{"internalType":"address","name":"onBehalfOf","type":"address"}],"name":"borrow","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"onBehalfOf","type":"address"},{"internalType":"uint16","name":"referralCode","type":"uint16"}],"name":"deposit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"balanceFromBefore","type":"uint256"},{"internalType":"uint256","name":"balanceToBefore","type":"uint256"}],"name":"finalizeTransfer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"receiverAddress","type":"address"},{"internalType":"address[]","name":"assets","type":"address[]"},{"internalType":"uint256[]","name":"amounts","type":"uint256[]"},{"internalType":"uint256[]","name":"modes","type":"uint256[]"},{"internalType":"address","name":"onBehalfOf","type":"address"},{"internalType":"bytes","name":"params","type":"bytes"},{"internalType":"uint16","name":"referralCode","type":"uint16"}],"name":"flashLoan","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getAddressesProvider","outputs":[{"internalType":"contract ILendingPoolAddressesProvider","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getConfiguration","outputs":[{"components":[{"internalType":"uint256","name":"data","type":"uint256"}],"internalType":"struct DataTypes.ReserveConfigurationMap","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getReserveData","outputs":[{"components":[{"components":[{"internalType":"uint256","name":"data","type":"uint256"}],"internalType":"struct DataTypes.ReserveConfigurationMap","name":"configuration","type":"tuple"},{"internalType":"uint128","name":"liquidityIndex","type":"uint128"},{"internalType":"uint128","name":"variableBorrowIndex","type":"uint128"},{"internalType":"uint128","name":"currentLiquidityRate","type":"uint128"},{"internalType":"uint128","name":"currentVariableBorrowRate","type":"uint128"},{"internalType":"uint128","name":"currentStableBorrowRate","type":"uint128"},{"internalType":"uint40","name":"lastUpdateTimestamp","type":"uint40"},{"internalType":"address","name":"aTokenAddress","type":"address"},{"internalType":"address","name":"stableDebtTokenAddress","type":"address"},{"internalType":"address","name":"variableDebtTokenAddress","type":"address"},{"internalType":"address","name":"interestRateStrategyAddress","type":"address"},{"internalType":"uint8","name":"id","type":"uint8"}],"internalType":"struct DataTypes.ReserveData","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getReserveNormalizedIncome","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getReserveNormalizedVariableDebt","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getReservesList","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"getUserAccountData","outputs":[{"internalType":"uint256","name":"totalCollateralETH","type":"uint256"},{"internalType":"uint256","name":"totalDebtETH","type":"uint256"},{"internalType":"uint256","name":"availableBorrowsETH","type":"uint256"},{"internalType":"uint256","name":"currentLiquidationThreshold","type":"uint256"},{"internalType":"uint256","name":"ltv","type":"uint256"},{"internalType":"uint256","name":"healthFactor","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"getUserConfiguration","outputs":[{"components":[{"internalType":"uint256","name":"data","type":"uint256"}],"internalType":"struct DataTypes.UserConfigurationMap","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"address","name":"aTokenAddress","type":"address"},{"internalType":"address","name":"stableDebtAddress","type":"address"},{"internalType":"address","name":"variableDebtAddress","type":"address"},{"internalType":"address","name":"interestRateStrategyAddress","type":"address"}],"name":"initReserve","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract ILendingPoolAddressesProvider","name":"provider","type":"address"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"collateralAsset","type":"address"},{"internalType":"address","name":"debtAsset","type":"address"},{"internalType":"address","name":"user","type":"address"},{"internalType":"uint256","name":"debtToCover","type":"uint256"},{"internalType":"bool","name":"receiveAToken","type":"bool"}],"name":"liquidationCall","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"address","name":"user","type":"address"}],"name":"rebalanceStableBorrowRate","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"rateMode","type":"uint256"},{"internalType":"address","name":"onBehalfOf","type":"address"}],"name":"repay","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"configuration","type":"uint256"}],"name":"setConfiguration","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bool","name":"val","type":"bool"}],"name":"setPause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"address","name":"rateStrategyAddress","type":"address"}],"name":"setReserveInterestRateStrategyAddress","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"bool","name":"useAsCollateral","type":"bool"}],"name":"setUserUseReserveAsCollateral","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"rateMode","type":"uint256"}],"name":"swapBorrowRateMode","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"to","type":"address"}],"name":"withdraw","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}]
    
    # Create contract instance
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    return contract

#returns our lists
def user_data(user_address, events, enum_name):
    df = pd.DataFrame()

    user_address_list = []
    tx_hash_list = []
    timestamp_list = []
    token_address_list = []
    token_volume_list = []
    token_usd_amount_list = []
    lend_borrow_type_list = []

    user = ''

    for event in events:
        # print(event)
        # print(event.args)
        # print(event)
        # print(f"Block Number: {event['blockNumber']}:")
        # print(f"{event['args']['onBehalfOf']}")
        if enum_name == 'REPAY':
            user = 'repayer'
        elif enum_name == 'COLLATERALISE':
            user = 'user'
        else:
            user = 'onBehalfOf'
        
        if enum_name != 'COLLATERALISE':
            if event['args'][user] == user_address:
                block = web3.eth.get_block(event['blockNumber'])

                user_address_list.append(event['args'][user])
                tx_hash_list.append(event['transactionHash'].hex())
                timestamp_list.append(block['timestamp'])
                token_address_list.append(event['args']['reserve'])
                token_volume_list.append(event['args']['amount'])
                token_usd_amount_list.append(get_tx_usd_amount(event['args']['reserve'], (event['args']['amount'])))
                lend_borrow_type_list.append(enum_name)
        
        else:
            if event['args'][user] == user_address:
                block = web3.eth.get_block(event['blockNumber'])

                user_address_list.append(event['args'][user])
                tx_hash_list.append(event['transactionHash'].hex())
                timestamp_list.append(block['timestamp'])
                token_address_list.append(event['args']['reserve'])
                token_volume_list.append(0)
                token_usd_amount_list.append(0)
                lend_borrow_type_list.append(enum_name)
    # i = 0

    # while i < len(user_address_list):
    #     print('user: ' + user_address_list[i])
    #     print('tx_hash: ' + tx_hash_list[i])
    #     print('timestamp: ' + str(timestamp_list[i]))
    #     print('token_address: ' + token_address_list[i])
    #     print('token_volume: ' + str(token_volume_list[i]))
    #     print('token_usd_amount: ' + str(token_usd_amount_list[i]))
    #     print('lendBorrowType: ' + lend_borrow_type_list[i])
    #     print('')

    #     i += 1

    df['wallet_address'] = user_address_list
    df['txHash'] = tx_hash_list
    df['timestamp'] = timestamp_list
    df['tokenAddress'] = token_address_list
    df['tokenVolume'] = token_volume_list
    df['tokenUSDAmount'] = token_usd_amount_list
    df['lendBorrowType'] = lend_borrow_type_list

    return df

#gets all of our borrow transactions
def get_borrow_transactions(user_address, contract):

    latest_block = web3.eth.get_block_number()
    from_block = latest_block - 100000
    from_block = 0

    events = contract.events.Borrow.get_logs(fromBlock=from_block, toBlock='latest')

    df = user_data(user_address, events, 'BORROW')

    return df

#gets all of our deposit transactions
def get_lend_transactions(user_address, contract):

    latest_block = web3.eth.get_block_number()
    from_block = latest_block - 100000
    from_block = 0

    events = contract.events.Deposit.get_logs(fromBlock=from_block, toBlock='latest')

    df = user_data(user_address, events, 'LEND')

    return df

#gets all of our repayment transactions
def get_repay_transactions(user_address, contract):

    latest_block = web3.eth.get_block_number()
    from_block = latest_block - 100000
    from_block = 0

    events = contract.events.Repay.get_logs(fromBlock=from_block, toBlock='latest')

    df = user_data(user_address, events, 'REPAY')

    return df

def get_collateralalise_transactions(user_address, contract):
    
    latest_block = web3.eth.get_block_number()
    from_block = latest_block - 100000
    from_block = 0

    events = contract.events.ReserveUsedAsCollateralEnabled.get_logs(fromBlock=from_block, toBlock='latest')

    df = user_data(user_address, events, 'COLLATERALISE')

    return df

#takes in our user address and will populate all the needed fields for our api_response
def get_all_user_transactions(user_address):
    df = pd.DataFrame()

    df_list = []

    contract = get_contract()

    borrow_df = get_borrow_transactions(user_address, contract)
    lend_df = get_lend_transactions(user_address, contract)
    repay_df = get_repay_transactions(user_address, contract)
    collateralize_df = get_collateralalise_transactions(user_address, contract)

    df_list = [borrow_df, lend_df, repay_df, collateralize_df]

    df = pd.concat(df_list)


    return df

# formats our dataframe response
def make_api_response_string(df):
    temp_df = df[['txHash', 'timestamp', 'tokenAddress', 'tokenVolume', 'tokenUSDAmount', 'lendBorrowType']]
    # Process data
    data = []
    for i in range(temp_df.shape[0]):
        row = temp_df.iloc[i]
        data.append({
            "txHash": str(row['txHash']),
            "timestamp": int(row['timestamp']),
            "tokenAddress": str(row['tokenAddress']),
            "tokenVolume": str(row['tokenVolume']),
            "tokenUSDAmount": float(row['tokenUSDAmount']),
            "lendBorrowType": str(row['lendBorrowType'])
        })

    # Create JSON response
    response = {
        "error": {
            "code": 0,
            "message": "success"
        },
        "data": {
            "result": data
        }
    }
    
    return response

# @app.route("/transactions/<address>", methods=["GET"])
# def balance_of(address):
    
#     df = get_all_user_transactions(address)
#     # out = df.to_json(orient='records')[1:-1].replace('},{', '} {')

#     response = make_api_response_string(df)

#     print(type(response))
#     # Return the balance in JSON format
#     # return jsonify(out)
#     return json.dumps(response), 200

@app.route("/transactions/", methods=["POST"])
def get_transactions():
    data = request.get_json()

    print(data)
    address = data['address']
    print(address)

    df = get_all_user_transactions(address)
    # out = df.to_json(orient='records')[1:-1].replace('},{', '} {')

    response = make_api_response_string(df)

    # print(type(response))
    # Return the balance in JSON format
    # return jsonify(out)
    return json.dumps(response), 200

if __name__ == "__main__":
    app.run(debug=True)

# @app.route("/transactions/<address>", methods=["POST"])
# def get_txns():
#     data = json.loads(request.data)
#     address = data['address'].lower()

#     df = get_all_user_transactions(address)
#     # out = df.to_json(orient='records')[1:-1].replace('},{', '} {')

#     response = make_api_response_string(df)

#     print(type(response))
#     # Return the balance in JSON format
#     # return jsonify(out)
#     return json.dumps(response)

# if __name__ == "__main__":
#     api_thread = threading.Thread(target=app.run(debug=True))
#     api_thread.start()

#     # app.run(debug=True)

#     data = {"address": "0x7B901f40228fC5cA87A288a7C1E88Bc439741fCF"}
#     # response = requests.post('http://127.0.0.1:5000/transactions/', data=data)
#     response = requests.post('http://127.0.0.1:5000/transactions/', data=json.dumps({'address': '0x7B901f40228fC5cA87A288a7C1E88Bc439741fCF'}))
#     print(response.text)
#     api_thread.join()
