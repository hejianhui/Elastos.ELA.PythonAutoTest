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
from .util import (
    assert_equal,
    rpc_port,
    rest_port,
    p2p_port,
    get_rpc_proxy,
    rpc_url,
    update_config,
)
from .authproxy import JSONRPCException

dev_null = open(os.devnull, 'w')


class Node(object):
    '''
    A class for representing a Elastos node.

    This class contains:

    - state about the node (whether the node is running, etc)
    - a Python subprocess.Popen object representing the running process
    - an RPC connection to the node
    - an Restful connection to the node
    - one or more P2P connections to the node

    To make things easier for the test writer, any unrecognized messages
    will be dispatched to the RPC and Restful connections.
    '''

    def __init__(self, i, dirname, host, timewait, binary, stderr, spv=False, mocktime=60, coverage_dir=None,
                 extra_conf=None, extra_args=None, use_cli=False):
        # coverage_dir用于保存log信息，暂未使用
        self.index = i
        if not spv:
            self.datadir = os.path.join(dirname, "node" + str(i))
        else:
            self.datadir = os.path.join(dirname, "spv" + str(i))
        print(i, self.datadir)

        # rpchost用于构建get_rpc_proxy实例
        # self.rpchost = rpchost if rpchost else None
        if timewait:
            self.rpc_timeout = timewait
        else:
            # Wait for up to 60 seconds for the RPC server to respond
            self.rpc_timeout = 60
        if binary is None:
            self.binary = config.node_name
        else:
            self.binary = binary
        self.stderr = stderr
        # self.coverage_dir = coverage_dir
        # self.coverage_dir = None
        if extra_conf != None:
            update_config(self.datadir, extra_conf)

        self.running = False
        self.process = None
        self.port_rpc = rpc_port(i)
        self.port_rest = rest_port(i)
        self.port_p2p = p2p_port(i)
        self.url = "http://127.0.0.1" + ":" + str(self.port_rpc)

        self.log = logging.getLogger('TestFramework.node%d' % i)

        # To enable when the p2p method is done
        self.p2ps = []

    # def __getattr__(self, name):
    #     """Dispatches any unrecognised messages to the RPC connection or a restful interface."""
    #     if self.running:
    #         return getattr(self.rpc, name)

    def start(self):
        """Start the node"""
        self.process = subprocess.Popen('./' + self.binary, stdout=dev_null, shell=True, cwd=self.datadir)
        self.running = True
        self.log.debug("%s started, waiting for RPC to come up" % self.binary)

    def stop(self):
        """stop the node"""
        if not self.running:
            return
        self.log.debug("Stopping node")
        try:
            # self.stop()
            self.process.terminate()
            # self.process.kill()
        # except http.client.CannotSendRequest:
        except subprocess.SubprocessError as e:
            self.log.exception("Unable to stop node. %s" % e)
        # self.running = False
        del self.p2ps[:]
        self.running = False

    def is_node_stopped(self):
        """Checks whether the node has stopped.

        Returns True if the node has stopped. False otherwise.
        This method is responsible for freeing resources (self.process)."""
        if not self.running:
            return True
        return_code = self.process.poll()
        print("node return code is", return_code)
        if return_code is None:
            return False

        # process has stopped. Assert that it didn't return an error code.
        assert_equal(return_code, 0)
        self.running = False
        self.process = None
        self.log.debug("Node stopped")
        return True

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
    '''
    A class for representing a Elastos SPV node.

    This class contains:

    - state about the node (whether the node is running, etc)
    - a Python subprocess.Popen object representing the running process
    - an RPC connection to the node
    - an Restful connection to the node
    - one or more P2P connections to the node

    To make things easier for the test writer, any unrecognized messages
    will be dispatched to the RPC and Restful connections.
    '''

    def __init__(self, i, dirname, host, timewait, binary, stderr, mocktime=60, coverage_dir=None, extra_conf=None,
                 extra_args=None, use_cli=False):
        # coverage_dir用于保存log信息，暂未使用
        self.index = i
        self.datadir = os.path.join(dirname, "spvnode" + str(i))
        print(i, self.datadir)

        # rpchost用于构建get_rpc_proxy实例
        # self.rpchost = rpchost if rpchost else None
        if timewait:
            self.rpc_timeout = timewait
        else:
            # Wait for up to 60 seconds for the RPC server to respond
            self.rpc_timeout = 60
        if binary is None:
            self.binary = config.svp_node_name
        else:
            self.binary = binary
        self.stderr = stderr
        # self.coverage_dir = coverage_dir
        # self.coverage_dir = None
        if extra_conf != None:
            update_config(self.datadir, extra_conf)

        self.running = False
        self.process = None
        self.port_rpc = rpc_port(i)
        self.port_rest = rest_port(i)
        self.port_p2p = p2p_port(i)
        self.url = "http://127.0.0.1" + ":" + str(self.port_rpc)

        self.log = logging.getLogger('TestFramework.node%d' % i)

        # To enable when the p2p method is done
        self.p2ps = []

    # def __getattr__(self, name):
    #     """Dispatches any unrecognised messages to the RPC connection or a restful interface."""
    #     if self.running:
    #         return getattr(self.rpc, name)

    def start(self):
        """Start the node"""
        self.process = subprocess.Popen('./' + self.binary, stdout=dev_null, shell=True, cwd=self.datadir)
        self.running = True
        self.log.debug("%s started, waiting for RPC to come up" % self.binary)

    def stop(self):
        """stop the node"""
        if not self.running:
            return
        self.log.debug("Stopping node")
        try:
            # self.stop()
            self.process.terminate()
            # self.process.kill()
        # except http.client.CannotSendRequest:
        except subprocess.SubprocessError as e:
            self.log.exception("Unable to stop node. %s" % e)
        # self.running = False
        del self.p2ps[:]
        self.running = False

    def is_node_stopped(self):
        """Checks whether the node has stopped.

        Returns True if the node has stopped. False otherwise.
        This method is responsible for freeing resources (self.process)."""
        if not self.running:
            return True
        return_code = self.process.poll()
        print("node return code is", return_code)
        if return_code is None:
            return False

        # process has stopped. Assert that it didn't return an error code.
        assert_equal(return_code, 0)
        self.running = False
        self.process = None
        self.log.debug("Node stopped")
        return True

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
