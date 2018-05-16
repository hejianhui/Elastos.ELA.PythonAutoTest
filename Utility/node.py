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

    def __init__(self, i, dirname, host, timewait, binary, stderr, mocktime=60, coverage_dir=None, extra_conf=None,
                 extra_args=None, use_cli=False):
        # coverage_dir用于保存log信息，暂未使用
        self.index = i
        self.datadir = os.path.join(dirname, "node" + str(i))
        print(i,self.datadir)

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
            update_config(dirname, i, extra_conf)

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

    def is_node_stopped(self):
        """Checks whether the node has stopped.

        Returns True if the node has stopped. False otherwise.
        This method is responsible for freeing resources (self.process)."""
        if not self.running:
            return True
        return_code = self.process.poll()
        if return_code is None:
            return False

        # process has stopped. Assert that it didn't return an error code.
        assert_equal(return_code, 0)
        self.running = False
        self.process = None
        self.log.debug("Node stopped")
        return True

    ## 封装的RPC方法，如RPC接口变更，对Method及Parameter进行相应修改即可
    def generate(self, n):
        resp = requests.post(self.url, json={"method": "manualmining", "params": {"count": n}},
                             headers={"content-type": "application/json"})
        return resp.json()['result']

    def get_block_count(self):
        resp = requests.post(self.url, json={"method": "getcurrentheight", "params": {}},
                             headers={"content-type": "application/json"})
        return resp.json()['result']

    def set_mining(self, mining):
        resp = requests.post(self.url, json={"method": "togglemining", "params": {"mining": mining}},
                             headers={"content-type": "application/json"})
        return resp.json()['result']

class Main():
    def __init__(self):
        pass


if __name__ == '__main__':
    pass
