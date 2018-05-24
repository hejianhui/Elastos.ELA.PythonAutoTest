from Utility import key_generator
from Utility import utility
import config

account1 = key_generator.Account("account1", "elastos")
account1.show_info()

account2 = key_generator.Account("account2", "elastos")
account2.show_info()

configuration_list = [
    {'name': 'ela', 'config': {
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
                'ActiveNet': 'RegNet'
            }
        }
    }},
    {'name': 'ela', 'config': {
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
                'PayToAddr': '8VYXVxKKSAxkmRrfmGpQR2Kc66XhG6m3ta',
                'AutoMining': False,
                'MinerInfo': 'ELA',
                'MinTxFee': 100,
                'ActiveNet': 'RegNet'
            }
        }
    }}
]
nodes = utility.deploy(configuration_list)

node1 = nodes[0]
node2 = nodes[1]
node1.start()
node2.start()
