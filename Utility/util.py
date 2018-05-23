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
PORT_INFO = 333
PORT_REST = 334
PORT_WS = 335
PORT_RPC = 336
PORT_P2P = 338
PORT_MINING = 339
# The number of port's interval
PORT_INTERVAL = 1000
SPV_INTERVAL = 10000


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


def info_port(n, spv=False):
    if spv:
        return PORT_MIN + PORT_INFO + n * PORT_INTERVAL + SPV_INTERVAL
    else:
        return PORT_MIN + PORT_INFO + n * PORT_INTERVAL


def ws_port(n, spv=False):
    if spv:
        return PORT_MIN + PORT_WS + n * PORT_INTERVAL + SPV_INTERVAL
    else:
        return PORT_MIN + PORT_WS + n * PORT_INTERVAL


def p2p_port(n, spv=False):
    assert (n <= MAX_NODES)
    if spv:
        return PORT_MIN + PORT_P2P + n * PORT_INTERVAL + SPV_INTERVAL
    else:
        return PORT_MIN + PORT_P2P + n * PORT_INTERVAL


def rest_port(n, spv=False):
    if spv:
        return PORT_MIN + PORT_REST + n * PORT_INTERVAL + SPV_INTERVAL
    else:
        return PORT_MIN + PORT_REST + n * PORT_INTERVAL


def rpc_port(n, spv=False):
    if spv:
        return PORT_MIN + PORT_RPC + n * PORT_INTERVAL + SPV_INTERVAL
    else:
        return PORT_MIN + PORT_RPC + n * PORT_INTERVAL


def mining_port(n, spv=False):
    if spv:
        return PORT_MIN + PORT_MINING + n * PORT_INTERVAL + SPV_INTERVAL
    else:
        return PORT_MIN + PORT_MINING + n * PORT_INTERVAL


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

def deploy(_num, _testpath, spv=False):
    # Get Node source path
    node_src_path = os.environ.get('GOPATH')
    for _path in config.node_src_path:
        node_src_path = os.path.join(node_src_path, _path)
        print(node_src_path)

    if not spv:
        # Deploy full node
        # Create base test directory
        # local = os.getcwd()
        tmpdir = "%s/elastos_test_runner_%s" % (_testpath, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        # tmpdir = "%s/elastos_test_runner" % _testpath
        os.makedirs(tmpdir)
        print("Temp dir is:", tmpdir, os.path.exists(tmpdir))

        for i in range(_num):
            _path = os.path.join(tmpdir, "node" + str(i))
            if not os.path.isdir(_path):
                os.makedirs(_path)

            shutil.copy(os.path.join(node_src_path, config.node_name), os.path.join(_path, config.node_name))
            shutil.copy(os.path.join(node_src_path, config.config_file), os.path.join(_path, 'config.json'))
            for pem_file in config.pem_file:
                shutil.copy(os.path.join(config.pem_path, pem_file), os.path.join(_path, pem_file))

        return tmpdir
    else:
        # Deploy exchange node
        if os.path.exists(_testpath):
            for i in range(_num):
                _path = os.path.join(_testpath, "spv" + str(i))
                if not os.path.isdir(_path):
                    os.makedirs(_path)

                shutil.copy(os.path.join(node_src_path, config.node_name), os.path.join(_path, config.node_name))
                shutil.copy(os.path.join(node_src_path, config.config_file), os.path.join(_path, 'config.json'))
            return _testpath
        else:
            os.makedirs(_testpath)
            for i in range(_num):
                _path = os.path.join(_testpath, "spv" + str(i))
                if not os.path.isdir(_path):
                    os.makedirs(_path)

                shutil.copy(os.path.join(node_src_path, config.node_name), os.path.join(_path, config.node_name))
                shutil.copy(os.path.join(node_src_path, config.config_file), os.path.join(_path, 'config.json'))
            return _testpath

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

    # json_str = json.dumps(config_json, sort_keys=True, indent=4, separators=(',', ':'))

    with open(os.path.join(nodedir, 'config.json'), 'w') as config_output:
        json.dump(config_json, config_output, sort_keys=True, indent=4, separators=(',', ':'))


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
    public_key = eccKey.public_key()

    redeem_script = key_gen.create_standard_redeem_script(public_key)
    program_hash = utility.script_to_program_hash(redeem_script)
    address = utility.program_hash_to_address(program_hash).encode()

    return address.decode(), eccKey._d, eccKey


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

# 批量生成地址，输出以address为key，private_key_int及ECCkey为value的字典
def generage_address(num):
    address_dict = {}
    for i in range(num):
        add, pk_int, ecc = get_new_address()
        address_dict[add] = {"pk_int": pk_int, "ecc": ecc}
    return address_dict

# 导出地址及ECCkey._d字典
def export_addresses(add_dict, path='./address.json'):
    if utility.is_file_exist(path):
        with open(path) as address_file:
            address_json = address_file.read()
            address_json = json.loads(address_json.strip())
            for add in add_dict.keys():
                if add in address_json.keys():
                    continue
                else:
                    address_json[add] = {"pk_int": str(add_dict[add]["pk_int"])}

        with open(path, 'w') as address_output:
            json.dump(address_json, address_output, sort_keys=True, indent=4, separators=(',', ':'))

    else:

        address_json = {}
        for add in add_dict.keys():
            address_json[add] = {"pk_int": str(add_dict[add]["pk_int"])}
        print(address_json)
        with open(path, 'w') as address_output:
            json.dump(address_json, address_output, sort_keys=True, indent=4, separators=(',', ':'))

def import_addresses(path='./address.json'):
    if not os.path.exists(path):
        print("There is no backup file address.json")
        return None
    else:
        with open(path,'r') as address_file:
            address_json = address_file.read()
            address_json = json.loads(address_json.strip())
            print(type(address_json),address_json)
        return address_json

class Main():
    def __init__(self):
        pass


if __name__ == '__main__':
    pass
