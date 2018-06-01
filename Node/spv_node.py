import subprocess
import logging
import config
import os
from utility import utility


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
