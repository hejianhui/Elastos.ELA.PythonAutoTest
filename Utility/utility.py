"""
Created on Apr 11, 2018

@author: bopeng
"""
import os
import datetime
import json
import shutil
import config

from Crypto.Hash import SHA256
from Crypto.Hash import RIPEMD160
import base58
from node import node
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


def script_to_program_hash(signature_redeem_script_bytes):
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
    double_value = SHA256.new(SHA256.new(data).digest()).digest()
    flag = double_value[0:4]
    data = data + flag
    encoded = base58.b58encode(data)
    return encoded


def address_to_programhash(address):
    return base58.b58decode_check(address)


def write_var_unit(buf_bytes, value):
    if value < 0xfd:
        buf_bytes += value.to_bytes(1, 'little')
    elif value <= 0xffff:
        buf_bytes += bytes([0xfd])
        buf_bytes += value.to_bytes(2, 'little')
    elif value <= 0xffffffff:
        buf_bytes += bytes([0xfe])
        buf_bytes += value.to_bytes(4, 'little')
    else:
        buf_bytes += bytes([0xff])
        buf_bytes += value.to_bytes(8, 'little')
    return buf_bytes


def do_sign(transaction, wallet_key_info):
    ECC_key = wallet_key_info
    buf = transaction.serialize_unsigned()
    h = SHA256.new(buf)
    signer = DSS.new(ECC_key, 'fips-186-3')
    signed_data = signer.sign(h)
    return signed_data


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


def encode_point(is_compressed, public_key_ECC):
    public_key_x = public_key_ECC._point._x
    public_key_y = public_key_ECC._point._y

    if public_key_x is None or public_key_y is None:
        infinity = []
        for i in range(INFINITYLEN):
            infinity.append(EMPTYBYTE)
        return infinity
    encodedData = []
    if is_compressed:
        for i in range(COMPRESSEDLEN):
            encodedData.append(EMPTYBYTE)
    else:
        for i in range(NOCOMPRESSEDLEN):
            encodedData.append(EMPTYBYTE)
        y_bytes = public_key_y.to_bytes()
        for i in range(NOCOMPRESSEDLEN - len(y_bytes), NOCOMPRESSEDLEN):
            encodedData[i] = y_bytes[i - NOCOMPRESSEDLEN + len(y_bytes)]
    x_bytes = public_key_x.to_bytes()
    l = len(x_bytes)
    for i in range(COMPRESSEDLEN - l, COMPRESSEDLEN):
        encodedData[i] = x_bytes[i - COMPRESSEDLEN + l]

    if is_compressed:
        if public_key_y % 2 == 0:
            encodedData[0] = COMPEVENFLAG
        else:
            encodedData[0] = COMPODDFLAG
    else:
        encodedData[0] = NOCOMPRESSEDFLAG
    return bytes(encodedData)
