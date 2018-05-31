#!/usr/bin/env python
# encoding: utf-8

"""
@author: Bocheng.Zhang
@license: Apache Licence 
@contact: bocheng0000@gmail.com
@file: Node.py
@time: 2018/5/9 16:23
"""

import logging
import os
import subprocess

import config
from Utility import utility
from Utility import jsonrpc

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

    def __init__(self, i, dirname, configuration: dict):
        self.index = i
        self.datadir = os.path.join(dirname, "ela" + str(i))

        print(i, self.datadir)
        self.configuration = configuration
        print(self.configuration)
        self.jsonrpc = jsonrpc.JSONRPC('http://127.0.0.1:' + str(configuration['HttpJsonPort']))
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
            return None

        self.log.info("Stopping node")
        self.process.terminate()
        self._running = False


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
        self.index = i
        self.datadir = os.path.join(dirname, "spvnode" + str(i))
        print(i, self.datadir)

        self.rpc_timeout = rpc_timeout
        self.name = config.SPV_NODE_NAME

        self._running = False
        self.process = None
        self.rpc_port = utility.rpc_port(i)
        self.rest_port = utility.rest_port(i)
        self.p2p_port = utility.p2p_port(i)

        self.log = logging.getLogger('TestFramework.node%d' % i)

        # To enable when the p2p method is done
        self.p2ps = []

    def is_running(self):
        return self._running

    def start(self):
        """Start the node"""
        self.process = subprocess.Popen('./' + self.name, stdout=DEV_NULL, shell=True, cwd=self.datadir)
        self._running = True
        self.log.debug("%s started, waiting for RPC to come up" % self.name)

    def stop(self):
        """stop the node"""
        if not self._running:
            return
        self.log.info("Stopping node")
        try:
            self.process.terminate()
        except subprocess.SubprocessError as e:
            self.log.exception("Unable to stop node. %s" % e)
        # self.running = False
        del self.p2ps[:]
        self._running = False
