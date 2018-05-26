#  a stress test script used in test net.

from Utility import account
from Utility import utility
from Wallet import wallet
import time

ACCOUNT_COUNT = 1000

account0 = account.Account("account0", "elatest")
wallet0 = wallet.Wallet(account0)

configuration_list = [
    {
        'name': 'ela',
        'config': {
            'Configuration': {
                'Magic': 1234567,
                'Version': 23,
                'SeedList': [
                    '127.0.0.1:10338',
                    '127.0.0.1:20338'
                ],
                'HttpInfoPort': 20333,
                'HttpInfoStart': True,
                'HttpRestPort': 20334,
                'HttpWsPort': 20335,
                'WsHeartbeatInterval': 60,
                'HttpJsonPort': 20336,
                'NodePort': 20338,
                'NodeOpenPort': 20866,
                'OpenService': False,
                'PrintLevel': 0,
                'IsTLS': False,
                'MultiCoreNum': 4,
                'MaxTransactionInBlock': 10000,
                'MaxBlockSize': 8000000,
                'PowConfiguration': {
                    'PayToAddr': account0.address,
                    'AutoMining': True,
                    'MinerInfo': 'ELA',
                    'MinTxFee': 0,
                    'ActiveNet': 'MainNet'
                }
            }
        }
    }
]
node = utility.deploy(configuration_list)[0]
node.start()
account_list = []

# generate account objects dynamically
account_names = locals()
for i in range(ACCOUNT_COUNT):
    account_list.append(account.Account("account" + str(i), "elatest"))
    print(account_list[i].address)

current_block_height = node.jsonrpc.getblockcount()
print("current block count is:", node.jsonrpc.getblockcount())
# generate one block, send ela to account0's address
while True:
    time.sleep(1)
    new_block_height = node.jsonrpc.getblockcount()
    if new_block_height > current_block_height:
        current_block_height = new_block_height
        print("new count is:", new_block_height)
        balance = wallet0.get_utxo_by_address("http://127.0.0.1", 20334, account0.address)
        break

tx = wallet0.create_transaction(
    from_address=account0.address,
    to_addresses=map(lambda x: x.address, account_list),
    amount=0.001,
    fee=0.001
)

signed_tx = wallet0.sign_standard_transaction("any", tx)
print(wallet0.send_transaction(signed_tx))
print("multi-output transaction is sent.")
print("current block count is:", node.jsonrpc.getblockcount())

while True:
    time.sleep(1)
    new_block_height = node.jsonrpc.getblockcount()

    print("current block count is:", new_block_height)
    if new_block_height > current_block_height + 10:
        break

while True:
    print("begin batch transactions")
    time_before = time.time()
    for i in range(ACCOUNT_COUNT):

        if i == ACCOUNT_COUNT - 1:
            from_index = i
            to_index = 0
        else:
            from_index = i
            to_index = i + 1
        # print(account_list[from_index])
        from_wallet = wallet.Wallet(account_list[from_index])
        tx = from_wallet.create_transaction(
            from_address=account_list[from_index].address,
            to_addresses=[account_list[to_index].address],
            amount=0.00001,
            fee=0
        )
        signed_tx = from_wallet.sign_standard_transaction("any", tx)
        resp = from_wallet.send_transaction(signed_tx)
        print("send small tx", resp)
    time_after = time.time()
    print("time span:", time_after - time_before)
    while True:
        time.sleep(1)
        new_block_height = node.jsonrpc.getblockcount()
        if new_block_height > current_block_height:
            current_block_height = new_block_height
            print("current block count is:", new_block_height)
            break
