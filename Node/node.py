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

from server import jsonrpc

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
