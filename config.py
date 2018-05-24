#!/usr/bin/env python
# encoding: utf-8

"""
@author: Bocheng.Zhang
@license: Apache Licence 
@contact: bocheng0000@gmail.com
@file: config.py
@time: 2018/5/9 14:54
"""

NODE_NAME = 'ela'

ELASTOS_PATH = ['src', 'github.com', 'elastos']
ELA_PATH = ELASTOS_PATH + ['Elastos.ELA']
SPV_PATH = ELASTOS_PATH + ['Elastos.ELA.SPV']
SPV_NODE_PATH = ELASTOS_PATH + ['Elastos.ELA.SPV.Node']
SIDECHAIN_PATH = ELASTOS_PATH + ['Elastos.ELA.SideChain']
ARBITER_PATH = ELASTOS_PATH + ['Elastos.ELA.Arbiter']

SPV_NODE_NAME = 'service'
SPV_CONFIGURATION_FILE = 'config.json'
TEST_PATH = './test'

DEFAULT_CONFIG_FILE = {
    'Configuration': {
        'Magic': 1234567,
        'Version': 23,
        'SeedList': [],
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
}
