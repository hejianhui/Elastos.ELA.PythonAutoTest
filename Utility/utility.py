'''
Created on Apr 11, 2018

@author: bopeng
'''
import os
from Crypto.Hash import SHA256
from Crypto.Hash import RIPEMD160
import binascii
from Utility import base58
from Crypto.Signature import DSS
import struct

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


def address_to_unit168(address):
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
