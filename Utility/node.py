#!/usr/bin/env python
# encoding: utf-8

"""
@author: Bocheng.Zhang
@license: Apache Licence 
@contact: bocheng0000@gmail.com
@file: Node.py
@time: 2018/5/9 16:23
"""

import errno
import http.client
import json
import logging
import os
import requests
import subprocess
import time
import urllib.parse

import config
from Utility import utility
from .authproxy import JSONRPCException

DEV_NULL = open(os.devnull, 'w')
ELA_NODE_NAME = 'ela'


class Node(object):
    """
    A class for representing a Elastos node.

    This class contains:

    - state about the node (whether the node is running, etc)
    - a Python subprocess.Popen object representing the running process
    - an RPC connection to the node
    - an Restful connection to the node
    - one or more P2P connections to the node

    To make things easier for the test writer, any unrecognized messages
    will be dispatched to the RPC and Restful connections.
    """

    def __init__(self, i, dirname, httptimeout=30, configuration={}):
        # coverage_dir用于保存log信息，暂未使用
        self.index = i
        self.datadir = os.path.join(dirname, "ela" + str(i))

        print(i, self.datadir)

        # rpchost用于构建get_rpc_proxy实例
        # self.rpchost = rpchost if rpchost else None
        self.rpc_timeout = httptimeout
        self._running = False
        self.process = None
        self.configuration = configuration

        self.log = logging.getLogger('TestFramework.node%d' % i)

    def is_running(self):
        return self._running

    def start(self):
        """Start the node"""
        self.process = subprocess.Popen('./' + ELA_NODE_NAME, stdout=DEV_NULL, shell=True, cwd=self.datadir)
        self._running = True
        self.log.info("ela node %s started, waiting for RPC to come up" % self.index)

    def stop(self):
        """stop the node"""
        if not self._running:
            self.log.info("warning: node is already stopped, does not need to stop anymore.")
            return
        self.log.info("Stopping node")
        try:
            # self.stop()
            self.process.terminate()
            # self.process.kill()
        # except http.client.CannotSendRequest:
        except subprocess.SubprocessError as e:
            self.log.exception("Unable to stop node. %s" % e)
        # self.running = False
        self._running = False

    ### 封装的RPC方法，如RPC接口变更，对Method及Parameter进行相应修改即可
    ## Interface for mining
    def generate(self, n):
        resp = requests.post(self.url, json={"method": "discretemining", "params": {"count": n}},
                             headers={"content-type": "application/json"})
        return resp.json()['result']

    # 设置节点是否开启挖矿
    def set_mining(self, mining):
        resp = requests.post(self.url, json={"method": "togglemining", "params": {"mining": mining}},
                             headers={"content-type": "application/json"})
        return resp.json()['result']

    ## Interface for querying information
    # 获取节点当前高度，目前节点无此接口，通过
    # def get_height(self):
    #     resp = requests.post(self.url, json={"method": "getcurrentheight", "params": {}},
    #                          headers={"content-type": "application/json"})
    #     return resp.json()['result']

    # 获取节点所有区块数，比高度多1，因创世区块高度为0
    def get_block_count(self):
        resp = requests.post(self.url, json={"method": "getblockcount", "params": {}},
                             headers={"content-type": "application/json"})
        return resp.json()['result']

    # 获取当前最高区块的BlockHash
    def get_best_block_hash(self):
        resp = requests.post(self.url, json={"method": "getbestblockhash", "params": {}},
                             headers={"content-type": "application/json"})
        return resp.json()['result']

    # 根据BlockHash获取区块详情，formate：0返回原始16进制字符串，1区块交易信息中只返回txid，2返回交易的完整信息
    # 建议节点端需增加AuxPow内容的解析
    def get_block_by_hash(self, blockhash, verbosity=2):
        resp = requests.post(self.url,
                             json={"method": "getblock", "params": {"blockhash": blockhash, "verbosity": verbosity}},
                             headers={"content-type": "application/json"})
        return resp.json()

    # 根据区块高度查询区块详情，verbosity=2
    def get_block_by_height(self, height):
        resp = requests.post(self.url, json={"method": "getblockbyheight", "params": {"height": height}},
                             headers={"content-type": "application/json"})
        return resp.json()

    # 根据区块高度获取BlockHash
    def get_block_hash_by_height(self, height):
        resp = requests.post(self.url, json={"method": "getblockhash", "params": {"height": height}},
                             headers={"content-type": "application/json"})
        return resp.json()

    # 获取节点连接数
    def get_connection_count(self):
        resp = requests.post(self.url, json={"method": "getconnectioncount", "params": {}},
                             headers={"content-type": "application/json"})
        return resp.json()['result']

    # 获取节点交易池
    def get_transaction_pool(self):
        resp = requests.post(self.url, json={"method": "getrawmempool", "params": {}},
                             headers={"content-type": "application/json"})
        return resp.json()

    # 根据txid获取交易
    def get_raw_transaction(self, txid, verbose=True):
        resp = requests.post(self.url,
                             json={"method": "getrawtransaction", "params": {"txid": txid, "verbose": verbose}},
                             headers={"content-type": "application/json"})
        return resp.json()

    # 获取邻居节点信息
    #
    def get_neighbors(self):
        resp = requests.post(self.url, json={"method": "getneighbors", "params": {}},
                             headers={"content-type": "application/json"})
        return resp.json()

    # 获取节点状态
    def get_node_state(self):
        resp = requests.post(self.url, json={"method": "getnodestate", "params": {}},
                             headers={"content-type": "application/json"})
        return resp.json()

    # 发送交易
    def send_raw_transaction(self, data):
        resp = requests.post(self.url, json={"method": "sendrawtransaction", "params": {"data": data}},
                             headers={"content-type": "application/json"})
        return resp.json()

    # 提交区块
    def submit_block(self, block):
        resp = requests.post(self.url, json={"method": "submitblock", "params": {"block": block}},
                             headers={"content-type": "application/json"})
        return resp.json()

    # 根据高度获取
    def get_arbitrator_group_by_height(self, height):
        resp = requests.post(self.url, json={"method": "getarbitratorgroupbyheight", "params": {"height": height}},
                             headers={"content-type": "application/json"})
        return resp.json()

    # 根据交易Hash获取交易
    # 是否将hash改为txid
    def get_transaction_by_hash(self, txid):
        resp = requests.post(self.url, json={"method": "gettransaction", "params": {"hash": txid}},
                             headers={"content-type": "application/json"})
        return resp.json()

    # 获取节点信息，包括版本、区块高度、连接节点数
    #
    def get_info(self):
        resp = requests.post(self.url, json={"method": "getinfo", "params": {}},
                             headers={"content-type": "application/json"})
        return resp.json()

    # 设置log等级
    def setloglevel(self, level):
        resp = requests.post(self.url, json={"method": "setloglevel", "params": {"level": level}},
                             headers={"content-type": "application/json"})
        return resp.json()

    ## Restful接口
    # 查询地址余额，直接返回余额对应的字符串
    def get_balance(self, address):
        resp = requests.get("http://127.0.0.1:" + str(self.port_rest) + "/api/v1/asset/balances/" + address)
        resp = resp.json()
        if resp['Desc'] == 'Success':
            return resp['Result'], True
        else:
            return "", False


class SPVNode(object):
    """
    A class for representing a Elastos SPV node.

    This class contains:

    - state about the node (whether the node is running, etc)
    - a Python subprocess.Popen object representing the running process
    - an RPC connection to the node
    - an Restful connection to the node
    - one or more P2P connections to the node

    To make things easier for the test writer, any unrecognized messages
    will be dispatched to the RPC and Restful connections.
    """

    def __init__(self, i, dirname, rpc_timeout=30, extra_conf=None):
        # coverage_dir用于保存log信息，暂未使用
        self.index = i
        self.datadir = os.path.join(dirname, "spvnode" + str(i))
        print(i, self.datadir)

        # rpchost用于构建get_rpc_proxy实例
        # self.rpchost = rpchost if rpchost else None
        self.rpc_timeout = rpc_timeout
        self.name = config.SPV_NODE_NAME

        if extra_conf != None:
            utility.update_config(self.datadir, extra_conf)

        self._running = False
        self.process = None
        self.rpc_port = utility.rpc_port(i)
        self.rest_port = utility.rest_port(i)
        self.p2p_port = utility.p2p_port(i)

        self.log = logging.getLogger('TestFramework.node%d' % i)

        # To enable when the p2p method is done
        self.p2ps = []

    # def __getattr__(self, name):
    #     """Dispatches any unrecognised messages to the RPC connection or a restful interface."""
    #     if self.running:
    #         return getattr(self.rpc, name)

    def is_running(self):
        return self._running

    def start(self):
        """Start the node"""
        self.process = subprocess.Popen('./' + self.binary, stdout=DEV_NULL, shell=True, cwd=self.datadir)
        self.running = True
        self.log.debug("%s started, waiting for RPC to come up" % self.binary)

    def stop(self):
        """stop the node"""
        if not self.running:
            return
        self.log.info("Stopping node")
        try:
            self.process.terminate()
        except subprocess.SubprocessError as e:
            self.log.exception("Unable to stop node. %s" % e)
        # self.running = False
        del self.p2ps[:]
        self.running = False

    ### 封装的RPC方法，如RPC接口变更，对Method及Parameter进行相应修改即可
    ## Interface for querying information
    # 获取节点当前高度，目前节点无此接口，通过
    # def get_height(self):
    #     resp = requests.post(self.url, json={"method": "getcurrentheight", "params": {}},
    #                          headers={"content-type": "application/json"})
    #     return resp.json()['result']

    ## Interface for registing addresses
    # 节点启动后批量注册地址
    def register_addresses(self, addresses):
        resp = requests.post(self.url, json={"method": "registeraddresses", "params": {"addresses": addresses}},
                             headers={"content-type": "application/json"})
        print(resp.json())
        return resp.json()

    # 节点启动后添加注册地址
    def register_address(self, address):
        resp = requests.post(self.url, json={"method": "registeraddress", "params": {"address": address}},
                             headers={"content-type": "application/json"})
        print(resp.json())
        return resp.json()

    ## 查询节点信息
    # 获取节点区块数量
    def get_block_count(self):
        resp = requests.post(self.url, json={"method": "getblockcount", "params": {}},
                             headers={"content-type": "application/json"})
        print(resp.json())
        return resp.json()

    # 获取当前最高区块的BlockHash
    def get_best_block_hash(self):
        resp = requests.post(self.url, json={"method": "getbestblockhash", "params": {}},
                             headers={"content-type": "application/json"})
        print(resp.json())
        return resp.json()['result']

    # 根据区块index获取区块hash
    def get_block_hash_by_index(self, index):
        resp = requests.post(self.url, json={"method": "getblockhash", "params": {"index": index}},
                             headers={"content-type": "application/json"})
        print(resp.json())
        return resp.json()['result']

    # # 根据BlockHash获取区块详情，formate：0返回原始16进制字符串，1区块交易信息中只返回txid，2返回交易的完整信息
    # # 建议节点端需增加AuxPow内容的解析
    def get_block_by_hash(self, blockhash, verbosity=2):
        resp = requests.post(self.url,
                             json={"method": "getblock", "params": {"hash": blockhash, "format": verbosity}},
                             headers={"content-type": "application/json"})
        return resp.json()

    # 根据区块高度查询区块详情，verbosity=2
    def get_block_by_height(self, height):
        resp = requests.post(self.url, json={"method": "getblockbyheight", "params": {"height": height}},
                             headers={"content-type": "application/json"})
        return resp.json()

    # 根据txid获取交易
    def get_raw_transaction(self, txid, verbose=1):
        resp = requests.post(self.url,
                             json={"method": "getrawtransaction", "params": {"hash": txid, "format": verbose}},
                             headers={"content-type": "application/json"})
        return resp.json()

    # 发送交易
    def send_raw_transaction(self, data):
        resp = requests.post(self.url, json={"method": "sendrawtransaction", "params": {"data": data}},
                             headers={"content-type": "application/json"})
        return resp.json()


if __name__ == '__main__':
    pass
