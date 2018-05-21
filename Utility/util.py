#!/usr/bin/env python
# encoding: utf-8

"""
@author: Bocheng.Zhang
@license: Apache Licence 
@contact: bocheng0000@gmail.com
@file: util.py
@time: 2018/5/7 10:30
"""

import os
import datetime
import json
import shutil
import time

import config

from .authproxy import AuthServiceProxy, JSONRPCException

from . import coverage
from . import key_generator
from . import utility


# Assert functions
##################

def assert_equal(thing1, thing2, *args):
    if thing1 != thing2 or any(thing1 != arg for arg in args):
        raise AssertionError("not(%s)" % " == ".join(str(arg) for arg in (thing1, thing2) + args))


# Utility functions
###################


# RPC/P2P connection constants and functions
############################################


# The maximum number of nodes a single test can spawn
MAX_NODES = 8
# Don't assign rpc or p2p ports lower than this
PORT_MIN = 10000
# The number of ports to "reserve" for p2p and rpc, each
PORT_REST = 334
PORT_RPC = 336
PORT_P2P = 338
# The number of port's interval
PORT_INTERVAL = 1000


class PortSeed:
    # Must be initialized with a unique integer for each process
    n = None


def get_rpc_proxy(url, node_number, timeout=None, coveragedir=None):
    """
    Args:
        url (str): URL of the RPC server to call
        node_number (int): the node number (or id) that this calls to

    Kwargs:
        timeout (int): HTTP timeout in seconds

    Returns:
        AuthServiceProxy. convenience object for making RPC calls.

    """
    proxy_kwargs = {}
    if timeout is not None:
        proxy_kwargs['timeout'] = timeout

    proxy = AuthServiceProxy(url, **proxy_kwargs)
    proxy.url = url  # store URL on proxy for info

    coverage_logfile = coverage.get_filename(
        coveragedir, node_number) if coveragedir else None

    return coverage.AuthServiceProxyWrapper(proxy, coverage_logfile)


def p2p_port(n):
    assert (n <= MAX_NODES)
    return PORT_MIN + PORT_P2P + n * PORT_INTERVAL


def rest_port(n):
    return PORT_MIN + PORT_REST + n * PORT_INTERVAL


def rpc_port(n):
    return PORT_MIN + PORT_RPC + n * PORT_INTERVAL


def rpc_url(i, rpchost=None):
    host = '127.0.0.1'
    port = rpc_port(i)
    if rpchost:
        parts = rpchost.split(':')
        if len(parts) == 2:
            host, port = parts
        else:
            host = rpchost
    return "http://%s:%d" % (host, int(port))


# Node functions
################

def deploy(_num, _testpath):
    # Get Node source path
    node_path = os.environ.get('GOPATH')
    for _path in config.node_src_path:
        node_path = os.path.join(node_path, _path)

    # store the nodes' port, path, etc
    nodes = {}

    # Create base test directory
    # local = os.getcwd()
    # tmpdir = "%s/elastos_test_runner_%s" % (_testpath, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    tmpdir = "%s/elastos_test_runner" % _testpath
    os.makedirs(tmpdir)

    # deploy ELAClient
    # _path = os.path.join(tmpdir, "Client", 'cli' + str(0))
    # if not os.path.isdir(_path):
    #     os.makedirs(_path)
    # shutil.copy(os.path.join(os.environ.get('GOPATH'), 'src', 'ELAClient', 'ela-cli'),
    #             os.path.join(_path, 'ela-cli'))
    # ela_config = {"LogToFile": False, "IpAddress": "localhost", "HttpJsonPort": 10336}
    # json_str = json.dumps(ela_config)
    # f = open(os.path.join(_path, 'cli-config.json'), 'w')
    # f.write(json_str)
    # f.close()

    # with open(
    #         os.path.join(node_path, config.config_file), "r+b") as fp:
    #     config_json = fp.read()
    #     config_json = config_json.decode("utf-8-sig")

    # file = open(os.path.join(os.environ.get('GOPATH'), 'src', 'Elastos.ELA', 'config.json'))
    # config_json = file.read()

    # if config_json.startswith(u'\ufeff'):
    #     config_json = config_json.encode('utf8')[3:].decode('utf8')

    # config_template = json.loads(config_json.strip())
    #
    for i in range(_num):
        _path = os.path.join(tmpdir, "Node" + str(i))
        if not os.path.isdir(_path):
            os.makedirs(_path)

        shutil.copy(os.path.join(node_path, config.node_name), os.path.join(_path, config.node_name))
        shutil.copy(os.path.join(node_path, config.config_file), os.path.join(_path, 'config.json'))
    return tmpdir
    #
    #     _config = {}
    #     _config['Path'] = _path
    #     _config['Magic'] = 20180000
    #     _config['SeedList'] = ["127.0.0.1:10338", "127.0.0.1:11338", "127.0.0.1:12338", "127.0.0.1:13338"]
    #
    #     _config['HttpInfoPort'] = i * 1000 + 10333
    #     _config['HttpRestPort'] = i * 1000 + 10334
    #     _config['HttpWsPort'] = i * 1000 + 10335
    #     _config['HttpJsonPort'] = i * 1000 + 10336
    #     _config['NodePort'] = i * 1000 + 10338
    #     _config['MiningSelfPort'] = i * 1000 + 10339
    #     _config['MultiCoreNum'] = 1
    #     _config['ActiveNet'] = 'MainNet'
    #     _config['PayToAddr'] = 'EPcqDUwUxJ96bTr6zB7tJnNXEN93JeBSKZ'
    #
    #     # if i == 0:
    #     #     _config['AutoMining'] = True
    #     # else:
    #     #     _config['AutoMining'] = False
    #
    #     _config['AutoMining'] = False
    #
    #     _node = Node(_config)
    #
    #     config_template['Configuration']['Magic'] = _node.magic
    #     config_template['Configuration']['SeedList'] = _node.seedList
    #     config_template['Configuration']['HttpInfoPort'] = _node.infoPort
    #     config_template['Configuration']['HttpRestPort'] = _node.restPort
    #     config_template['Configuration']['HttpWsPort'] = _node.wsPort
    #     config_template['Configuration']['HttpJsonPort'] = _node.jsonPort
    #     config_template['Configuration']['NodePort'] = _node.nodePort
    #     config_template['Configuration']['MiningSelfPort'] = _node.miningPort
    #     config_template['Configuration']['MultiCoreNum'] = _node.miningCoreNum
    #     config_template['Configuration']['PowConfiguration']['ActiveNet'] = _node.activeNet
    #     config_template['Configuration']['PowConfiguration']['PayToAddr'] = _node.address
    #     config_template['Configuration']['PowConfiguration']['AutoMining'] = _node.miningState
    #
    #     json_str = json.dumps(config_template)
    #     f = open(os.path.join(_path, 'config.json'), 'w')
    #     f.write(json_str)
    #     f.close()
    #
    #     nodes[i] = _node
    #
    # return nodes


def get_datadir_path(dirname, n):
    return os.path.join(dirname, "node" + str(n))


def update_config(nodedir, options):
    with open(os.path.join(nodedir, 'config.json'), "r+b") as config_file:
        config_json = config_file.read()
        config_json = json.loads(config_json.decode("utf-8-sig").strip())
        for config_key in options.keys():
            if isinstance(options[config_key], dict):
                for _key in options[config_key].keys():
                    config_json['Configuration'][config_key][_key] = options[config_key][_key]
            else:
                config_json['Configuration'][config_key] = options[config_key]

    json_str = json.dumps(config_json)
    with open(os.path.join(nodedir, 'config.json'), 'w') as config_output:
        config_output.write(json_str)
        config_output.close()


def sync_blocks(nodes, *, wait=1, timeout=60):
    """
    Wait until everybody has the same tip.

    sync_blocks needs to be called with an rpc_connections set that has least
    one node already synced to the latest, stable tip, otherwise there's a
    chance it might return before all nodes are stably synced.
    """
    stop_time = time.time() + timeout
    while time.time() <= stop_time:
        best_hash = [nodes[i].get_best_block_hash() for i in range(len(nodes))]
        if best_hash.count(best_hash[0]) == len(nodes):
            return
        time.sleep(wait)
    raise AssertionError("Block sync timed out:{}".format("".join("\n  {!r}".format(b) for b in best_hash)))


def get_new_address():
    key_gen = key_generator.Generator()
    eccKey = key_gen.create_key_pair()
    # private_key1 = eccKey.d.to_bytes()
    public_key = eccKey.public_key()

    redeem_script = key_gen.create_standard_redeem_script(public_key)

    program_hash = utility.script_to_program_hash(redeem_script)
    address = utility.program_hash_to_address(program_hash).encode()
    print(address.decode())
    print(eccKey._d)
    return address.decode(), eccKey._d


def restore_wallet(pk_int):
    key_gen = key_generator.Generator()
    eccKey = key_gen.create_public_key_with_private(pk_int)

    public_key = eccKey.public_key()

    redeem_script = key_gen.create_standard_redeem_script(public_key)

    program_hash = utility.script_to_program_hash(redeem_script)
    address = utility.program_hash_to_address(program_hash).encode()

    print(address.decode())
    print(type(eccKey._d), eccKey._d)
    print(type(pk_int), pk_int)
    if eccKey._d != pk_int:
        print("Error")


class Main():
    def __init__(self):
        pass


if __name__ == '__main__':
    pass
