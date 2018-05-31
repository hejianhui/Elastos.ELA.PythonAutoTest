from Utility import account
from Utility import utility
from Wallet import wallet
import time

account1 = account.Account("foundationwallet1",
                           "eebfbd55819ea095107b776616669536d9f0bb6d3cd9b21665ea1fb02405cfed")
account1.show_info()
account2 = account.Account("foundationwallet2",
                           "927f1ff719047e0243150447b9c009fc2f17d67fd413beb965b9a9449d42b9b1")
account2.show_info()
account3 = account.Account("foundationwallet3",
                           "8d57d983f5960f6b3b2ed1d4f7350cfa7fb985580eaf4b9a2d8501384ce27369")
account3.show_info()
account4 = account.Account("foundationwallet4",
                           "22e388e026234863ba077fe18783bbf7935c49ed08898995e7f5f64db8d51cef")
account4.show_info()
foundation_account = account.MultiSignAccount(3, "name", "password",
                                              [account2.ECCkey, account1.ECCkey, account4.ECCkey, account3.ECCkey])
foundation_account.show_info()

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
                'HttpInfoPort': 10333,
                'HttpInfoStart': True,
                'HttpRestPort': 10334,
                'HttpWsPort': 10335,
                'WsHeartbeatInterval': 60,
                'HttpJsonPort': 10336,
                'NodePort': 10338,
                'NodeOpenPort': 10866,
                'FoundationAddress': '8ZNizBf4KhhPjeJRGpox6rPcHE5Np6tFx3',
                'OpenService': False,
                'PrintLevel': 0,
                'IsTLS': False,
                'MultiCoreNum': 4,
                'MaxTransactionInBlock': 10000,
                'MaxBlockSize': 8000000,
                'PowConfiguration': {
                    'PayToAddr': account1.address,
                    'AutoMining': False,
                    'MinerInfo': 'ELA',
                    'MinTxFee': 100,
                    'ActiveNet': 'MainNet'
                }
            }
        }},
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
                'FoundationAddress': '8ZNizBf4KhhPjeJRGpox6rPcHE5Np6tFx3',
                'OpenService': False,
                'PrintLevel': 0,
                'IsTLS': False,
                'MultiCoreNum': 4,
                'MaxTransactionInBlock': 10000,
                'MaxBlockSize': 8000000,
                'PowConfiguration': {
                    'PayToAddr': '8VYXVxKKSAxkmRrfmGpQR2Kc66XhG6m3ta',
                    'AutoMining': False,
                    'MinerInfo': 'ELA',
                    'MinTxFee': 100,
                    'ActiveNet': 'MainNet'
                }
            }
        }
    }
]
nodes = utility.deploy(configuration_list)

node0 = nodes[0]
node1 = nodes[1]
node0.start()
node1.start()
time.sleep(3)
# print(node0.jsonrpc.discretemining(count=2))

wallet1 = wallet.Wallet(account1)
wallet2 = wallet.Wallet(account2)
wallet3 = wallet.Wallet(account3)
wallet4 = wallet.Wallet(account4)

foundation_wallet = wallet.Wallet(foundation_account)

tx = foundation_wallet.create_transaction(foundation_account.address, [account1.address, account2.address], 1,
                                          0.00001)
tx = wallet1.sign_multi_transaction("any", tx)
tx = wallet2.sign_multi_transaction("any", tx)
tx = wallet3.sign_multi_transaction("any", tx)
tx = wallet4.sign_multi_transaction("any", tx)

print(wallet1.send_transaction(tx))

result = node0.jsonrpc.discretemining(count=1)

print(result)

single_tx = wallet1.create_transaction(account1.address, [account2.address], 0.01, 0.00001)
wallet1.sign_standard_transaction('any', single_tx)

print(result)

result = wallet1.send_transaction(single_tx)

print(result)
