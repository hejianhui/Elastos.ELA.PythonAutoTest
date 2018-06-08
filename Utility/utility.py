"""
Created on Apr 11, 2018

@author: bopeng
"""
import base58
import time
import re
from config import logger
from Crypto.Hash import SHA256
from Crypto.Hash import RIPEMD160
from Crypto.Signature import DSS

INFINITYLEN = 1
FLAGLEN = 1
XORYVALUELEN = 32
COMPRESSEDLEN = 33
NOCOMPRESSEDLEN = 65
COMPEVENFLAG = 0x02
COMPODDFLAG = 0x03
NOCOMPRESSEDFLAG = 0x04
# P256PARAMA = -3
EMPTYBYTE = 0x00

STANDARD = 0xac
MULTISIG = 0xae

CoinBase = bytes([0x00])
RegisterAsset = bytes([0x01])
TransferAsset = bytes([0x02])
Recrd = bytes([0x03])
PUSH1 = 0x51


def script_to_program_hash(signature_redeem_script_bytes: bytes):
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

    double_value = SHA256.new(hash_value_bytes)
    double_value_bytes = double_value.digest()
    return double_value_bytes


def program_hash_to_address(program_hash_bytes: bytes):
    data = program_hash_bytes
    double_value = SHA256.new(SHA256.new(data).digest()).digest()
    flag = double_value[0:4]
    data = data + flag
    encoded = base58.b58encode(data)
    return encoded


def address_to_programhash(address: str):
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


def sync_mempools(nodes: list()):
    time_out = 15
    while True:
        mempools = [node.jsonrpc.getrawmempool() for node in nodes]

        # remove duplicate, if all nodes' transaction pools is synced,
        # then the set has only one element.
        new_mempools = []
        for mempool in mempools:
            if mempool not in new_mempools:
                new_mempools.append(mempool)

        if len(new_mempools) == 1:
            break
        if time_out <= 0:
            raise AssertionError('transaction pool dose not synced, timeout.')
        time.sleep(1)
        time_out -= 1
        print('sync mempools time out:', time_out)


def sync_blocks(nodes: list()):
    time_out = 15
    while True:
        bestblockhashes = [node.jsonrpc.getbestblockhash()['result'] for node in nodes]
        logger.info('best block hashes:', bestblockhashes)
        bestblockhash = set(bestblockhashes)
        if len(bestblockhash) == 1:
            return

        if time_out <= 0:
            raise AssertionError('sync block failed.')

        time.sleep(1)
        time_out -= 1
        print('sync block time out:', time_out)


def camel_to_snake(class_name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
