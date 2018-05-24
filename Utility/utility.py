#!/usr/bin/env python3
# encoding: utf-8
"""
Created on Apr 11, 2018

@author: bopeng
"""
import os
import datetime
import json
import requests
import shutil
import time
import config

from . import account

from Crypto.Hash import SHA256
from Crypto.Hash import RIPEMD160
import binascii
from Utility import base58
from Utility import node
from Crypto.Signature import DSS

INFINITYLEN = 1
FLAGLEN = 1
XORYVALUELEN = 32
COMPRESSEDLEN = 33
NOCOMPRESSEDLEN = 65
COMPEVENFLAG = 0x02
COMPODDFLAG = 0x03
NOCOMPRESSEDFLAG = 0x04
P256PARAMA = -3
EMPTYBYTE = 0x00

STANDARD = 0xac
MULTISIG = 0xae

UINT168SIZE = 21

CoinBase = bytes([0x00])
RegisterAsset = bytes([0x01])
TransferAsset = bytes([0x02])
Recrd = bytes([0x03])
Deploy = bytes([0x04])
PUSH1 = 0x51

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


def is_file_exist(file_path):
    return os.path.exists(file_path)


def script_to_program_hash(signature_redeem_script_byte_list):
    signature_redeem_script_bytes = b''
    if "\\" in str(signature_redeem_script_byte_list):
        for b in signature_redeem_script_byte_list:
            signature_redeem_script_bytes = signature_redeem_script_bytes + b
    else:
        for b in signature_redeem_script_byte_list:
            b_v = int(str(b)[2:len(str(b)) - 1], 16)
            b_b = bytes([b_v])
            signature_redeem_script_bytes += b_b
    temp = SHA256.new(signature_redeem_script_bytes)
    md = RIPEMD160.new(data=temp.digest())
    f = md.digest()
    sign_type = signature_redeem_script_bytes[len(signature_redeem_script_bytes) - 1]
    if sign_type == STANDARD:
        f = bytes([33]) + f
    if sign_type == MULTISIG:
        f = bytes([18]) + f
    return f


def to_aes_key(data_bytes):
    hash_value = SHA256.new(data_bytes)
    hash_value_bytes = hash_value.digest()
    # print("first_hash " + binascii.b2a_hex(hash_value_bytes).decode("utf-8"))

    double_value = SHA256.new(hash_value_bytes)
    double_value_bytes = double_value.digest()
    # print("second_hash(aes_key) " + binascii.b2a_hex(double_value_bytes).decode("utf-8"))
    return double_value_bytes


def program_hash_to_address(program_hash_bytes):
    data = program_hash_bytes
    temp = SHA256.new(data)
    bin_temp_value = temp.digest()
    double_value = SHA256.new(bin_temp_value).digest()
    frag = double_value[0:4]
    data = data + frag
    encoded = base58.b58encode(data)
    return encoded


def address_to_programhash(address):
    decoded = base58.b58decode_check(address)
    ph = decoded[0:21]
    addr = program_hash_to_address(ph)
    if addr != address:
        print("[AddressToProgramHash]: decode address verify failed.")
        return
    return ph


def write_var_unit(buf_bytes, value):
    # reversed_value = reverse_values_bitwise(value)
    value_int = utf_to_rawint(value)
    if value_int < 0xfd:
        buf_bytes += value
        return buf_bytes
    elif value_int <= 0xffff:
        extended_value = add_zero(value, 16)
        reversed_value = reverse_values_bitwise(extended_value)
        buf_bytes += bytes([0xfd])
        buf_bytes += reversed_value
    elif value_int <= 0xffffffff:
        extended_value = add_zero(value, 32)
        reversed_value = reverse_values_bitwise(extended_value)
        buf_bytes += bytes([0xfe])
        buf_bytes += reversed_value
    else:
        extended_value = add_zero(value, 64)
        reversed_value = reverse_values_bitwise(extended_value)
        buf_bytes += bytes([0xff])
        buf_bytes += reversed_value
    return buf_bytes


def reverse_values_bitwise(n):
    if n == None:
        return 0
    if (type(n) is bytes) and "\\" in str(n):
        buf = b''
        for i in range(len(n)):
            index = len(n) - 1 - i
            temp = n[index]
            buf += bytes([temp])
        return buf

    min_bit_length = n.bit_length()
    width = min_bit_length + 4 - min_bit_length % 4
    b = '{:0{width}b}'.format(n, width=width)
    result = int(b[::-1], 2)
    return result


def bytes_to_hex_string(bytes_value):
    if bytes_value == None:
        return ""
    if "\\" in str(bytes_value):
        return binascii.b2a_hex(bytes_value).decode("utf-8")
    else:
        return str(bytes_value)[2:len(bytes_value) + 2]


def do_sign(transaction, wallet_key_info):
    ECC_key = wallet_key_info
    buf = transaction.serialize_unsigned()
    h = SHA256.new(buf)
    signer = DSS.new(ECC_key, 'fips-186-3')
    signed_data = signer.sign(h)
    return signed_data


def bytes_to_hex_value(bytes_value):
    return int('0x' + bytes_value.decode(), 16)


def bytelist_to_bytes(byte_list):
    buf = b''
    for b in byte_list:
        buf += b
    return buf


def valuebytes_to_valuebytelist(bytes_value):
    buf = []
    if len(bytes_value) % 2 != 0:
        print("Invalid bytes, need to have even length")
        return
    for i in range(int(len(bytes_value) / 2)):
        index = i * 2
        buf.append(bytes_value[index:index + 2])
    return buf


def valuebytes_to_utfbytes(bytes_value):
    value_list = valuebytes_to_valuebytelist(bytes_value)
    utf_bytes = b''
    for v in value_list:
        hex_string = bytes_to_hex_string(v)
        hex_value = int(hex_string, 16)
        utf_bytes += bytes([hex_value])
    return utf_bytes


def add_zero(bytes_value, expected_length):
    if len(bytes_value) == expected_length:
        return bytes_value
    if len(bytes_value) > expected_length:
        print("Out of limit length")
        return
    zero_to_add = expected_length - len(bytes_value)
    for _ in range(zero_to_add):
        bytes_value = bytes([0]) + bytes_value
    return bytes_value


def utf_to_rawint(value):
    result = 0
    for i in range(len(value)):
        digit = value[len(value) - i - 1]
        result += digit * 256 ** i
    return result


# Assert functions
##################

def assert_equal(thing1, thing2, *args):
    if thing1 != thing2 or any(thing1 != arg for arg in args):
        raise AssertionError("not(%s)" % " == ".join(str(arg) for arg in (thing1, thing2) + args))


# Utility functions
###################

def deploy(configuration_lists=list()):
    """
    this function receives a list of dictionary ,
    in which each dictionary is composed of node name and its configuration.
    and configuration is also a dictionary.
    :param configuration_lists:
    :return: list of node objects
    """

    project_path = os.environ.get('GOPATH') + '/'.join(config.ELA_PATH)
    print("source code path:", project_path)

    node_path = "%s/elastos_test_runner_%s" % ("./test", datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(node_path)
    print("Temp dir is:", node_path)
    nodes_list = []

    for index, item in enumerate(configuration_lists):
        name = item['name']
        path = os.path.join(node_path, name + str(index))
        os.makedirs(path)
        shutil.copy(os.path.join(project_path, name), os.path.join(path))
        configuration = item['config']
        with open(path + '/config.json', 'w+') as f:
            f.write(json.dumps(configuration, indent=4))

        nodes_list.append(node.Node(i=index, dirname=node_path, configuration=configuration['Configuration']))

    return nodes_list


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

    # json_str = json.dumps(config_json, sort_keys=False, indent=4, separators=(',', ':'))

    with open(os.path.join(nodedir, 'config.json'), 'w') as config_output:
        json.dump(config_json, config_output, sort_keys=False, indent=4, separators=(',', ':'))


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
    key_gen = account.Generator()
    eccKey = key_gen.create_key_pair()
    public_key = eccKey.public_key()

    redeem_script = key_gen.create_standard_redeem_script(public_key)
    program_hash = script_to_program_hash(redeem_script)
    address = program_hash_to_address(program_hash).encode()

    return address.decode(), eccKey._d, eccKey


def restore_wallet(pk_int):
    key_gen = account.Generator()
    eccKey = key_gen.create_public_key_with_private(pk_int)

    public_key = eccKey.public_key()

    redeem_script = key_gen.create_standard_redeem_script(public_key)

    program_hash = script_to_program_hash(redeem_script)
    address = program_hash_to_address(program_hash).encode()

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
    if is_file_exist(path):
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
        with open(path, 'r') as address_file:
            address_json = address_file.read()
            address_json = json.loads(address_json.strip())
            print(type(address_json), address_json)
        return address_json


def get_utxo(address):
    r = requests.get("http://127.0.0.1:10334/api/v1/asset/utxos/" + address)
    if r.json()['Desc'] == 'Success':
        for _list in r.json()['Result']:
            if _list['AssetName'] == 'ELA':
                return _list['Utxo']
    else:
        return []


def get_transaction(txid):
    r = requests.get("http://127.0.0.1:10334/api/v1/transaction/" + txid)
    if r.json()['Desc'] == 'Success':
        return r.json()['Result']
    else:
        return None


# 利用交易信息中的确认数判断UTXO是否可用，后续可更改为利用blockhash查询区块高度，进而判断UTXO是否可用
def utxo_filter(utxos):
    utxo_useful = []
    for utxo in utxos:
        txid = utxo["Txid"]
        trans = get_transaction(txid)
        if trans['confirmations'] > 100:
            utxo_useful.append(utxo)

    return utxo_useful


def get_useful_utxo(address):
    utxos = get_utxo(address)
    return utxo_filter(utxos)
