"""
Created on Mar 30, 2018

@author: bopeng
"""
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
import array
import binascii
import os
import json

from Utility import utility

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


class Account(object):
    """
    classdocs
    """

    def __init__(self, name="name", password="password", private_key=None, sign_type=STANDARD, m=0, n=0):

        """
        Constructor
        """
        self.public_key = None
        self.sign_script = None
        self.program_hash = None
        self.address = None
        self.private_key = None
        self.iv = os.urandom(16)
        self.master_key = os.urandom(32)
        self.name = name

    '''
    def decode_point(self, encoded_data):
        compressed_flag = encoded_data[0]
        x_bytes_len = 32
        x_bytes = b''
        y_bytes = b''
        for i in range(Generator.COMPRESSEDLEN - x_bytes_len, Generator.COMPRESSEDLEN): # 1 to 33
            x_bytes[i - 1] = encoded_data[i]
        x_long = bytes_to_long(x_bytes)
        y_long = 0
        if compressed_flag == 0x00:
            return None
        elif compressed_flag == 0x02 or compressed_flag == 0x03:
            #compressed
            return {"X":x_long, "Y":y_long}
        elif compressed_flag == 0x04 or compressed_flag == 0x06 or compressed_flag == 0x07:
            #no compressed
            for i in range(Generator.NOCOMPRESSEDLEN - len(y_bytes), Generator.NOCOMPRESSEDLEN):
                y_bytes[i - 33] = encoded_data[i]
                y_long = bytes_to_long(y_bytes)
            return {"X":x_long, "Y":y_long}
        return None
    '''

    '''
    def decode_point(self, encoded_data):
        if encoded_data[0] == 0x00:
            return {"X": None, "Y": None}
        elif encoded_data[0] == 0x02 or encoded_data[0] == 0x03:
            y_tilde = int(encoded_data[0] & 1)
            print("compressed\n")
            pub_key = self.decompress(y_tilde, encoded_data[FLAGLEN: FLAGLEN + XORYVALUELEN],
                                      self.ECCkey)
            return pub_key
        elif encoded_data[0] == 0x04 or encoded_data[0] == 0x05 or encoded_data[0] == 0x06:
            pub_key_x = encoded_data[FLAGLEN: FLAGLEN + XORYVALUELEN]
            pub_key_y = encoded_data[FLAGLEN + XORYVALUELEN: NOCOMPRESSEDLEN]
            return {"X": pub_key_x, "Y": pub_key_y}
        else:
            print("invalid encode data format")
            return None
    '''

    '''
    return a ECC type keypair
    '''

    def create_key_pair(self):
        ECCkey = ECC.generate(curve='P-256')
        return ECCkey

    '''
    return a ECC type keypair with the private key given as hex value
    '''

    def create_public_key_with_private(self, private_key_int):
        ECCkey = ECC.construct(curve='P-256', d=private_key_int)
        self.private_key = ECCkey.d.to_bytes()
        # print(ECCkey)
        self.ECCkey = ECCkey
        return ECCkey

    def create_standard_key_store(self, name, password, private_key=None):
        if not str(name).endswith(".json"):
            name = name + ".json"

        if os.path.isfile(name):
            print("key store file already exist")
            self.import_key_info(key_path=name)
            return

        iv_bytes = self.iv
        master_key_bytes = self.master_key
        password_key_bytes = utility.to_aes_key(str.encode(password))
        password_hash = SHA256.new(password_key_bytes)
        password_hash_bytes = password_hash.digest()
        self.password_hash_bytes = password_hash_bytes

        master_key_encrypted_bytes = self.encrypt_master_key(iv_bytes, password_key_bytes, master_key_bytes)
        self.master_key_encrypted_bytes = master_key_encrypted_bytes
        if private_key is None:
            key_pair = self.create_key_pair()
        else:
            key_pair = ECC.construct(curve='P-256', d=int(private_key, 16))

        self.ECCkey = key_pair

        private_key_int = key_pair._d
        private_key_bytes = private_key_int.to_bytes()
        private_key_byte_array = bytearray(private_key_bytes)
        self.private_key_byte_array = private_key_byte_array
        public_key_ECC = key_pair.public_key()

        private_key_encrypted_bytes = self.encrypt_private_key(master_key_bytes, private_key_bytes,
                                                               public_key_ECC, iv_bytes)
        self.private_key_encrypted_bytes = private_key_encrypted_bytes
        self.private_key = private_key_bytes

        # print("private_key: " + binascii.b2a_hex(self.private_key).decode())

        self.init_standard(public_key_ECC)

        self.store_wallet_data()

    def store_wallet_data(self):
        if not os.path.exists("./wallets"):
            os.mkdir("./wallets")

        attributes = dict(
            {
                'private_key': utility.bytes_to_hex_string(self.private_key),
                'public_key': utility.bytes_to_hex_string(self.public_key),
                'programhash': utility.bytes_to_hex_string(self.program_hash),
                'master_key': utility.bytes_to_hex_string(self.master_key),
                'iv': utility.bytes_to_hex_string(self.iv),
                'address': utility.bytes_to_hex_string(self.address)
            }
        )
        with open('./wallets/' + self.name + ".json", 'w') as f:
            f.write(json.dumps(attributes))

    def encrypt_master_key(self, iv, password_key, master_key):
        master_key_encrypted = self.aes_encrypt(master_key, password_key, iv)
        return master_key_encrypted

    def encrypt_private_key(self, master_key, private_key, public_key_ECC, iv):

        decrypted_private_key = []
        for i in range(96):
            decrypted_private_key.append(0x00)
        public_key_bytes = encode_point(False, public_key_ECC)

        for i in range(64):
            decrypted_private_key[i] = public_key_bytes[i + 1]
        for i in range(len(private_key) - 1, 0, -1):
            decrypted_private_key[96 + i - len(private_key)] = private_key[i]
        decrypted_private_key_bytes = array.array('B', decrypted_private_key).tobytes()

        encrypted_private_key = self.aes_encrypt(decrypted_private_key_bytes, master_key, iv)

        return encrypted_private_key

    def aes_encrypt(self, plaintext, key, iv):
        #         print("aes_key " + str(key) + "\n")
        cbc_cipher = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
        cbc_buffer = cbc_cipher.encrypt(plaintext)
        #         print (cbc_buffer)
        return cbc_buffer

    def init_standard(self, public_key_ECC):
        signature_redeem_script_byte_list = self.create_standard_redeem_script(public_key_ECC)
        program_hash = utility.script_to_program_hash(signature_redeem_script_byte_list)
        signature_redeem_script_bytes = b''
        for b in signature_redeem_script_byte_list:
            signature_redeem_script_bytes = signature_redeem_script_bytes + b
        reversed_program_hash = b''
        for b in bytearray(program_hash):
            reversed_program_hash = bytes([b]) + reversed_program_hash

        self.public_key = get_hex_public_key(public_key_ECC)
        self.sign_script = binascii.hexlify(signature_redeem_script_bytes)
        self.program_hash = binascii.hexlify(reversed_program_hash)
        self.address = utility.bytes_to_hex_string(utility.program_hash_to_address(program_hash).encode())

        # print("public_key: " + self.public_key.decode("utf-8"))
        # print("sign_script: " + self.sign_script.decode("utf-8"))
        # print("program_hash: " + self.program_hash.decode("utf-8"))
        # print("address: " + self.address.decode())

    def create_standard_redeem_script(self, public_key_ECC):
        content = encode_point(True, public_key_ECC)
        buf = []
        buf.append(bytes([len(content)]))
        for i in range(len(content)):
            buf.append(bytes([content[i]]))
        buf.append(bytes([STANDARD]))
        return buf

    def show_info(self):
        print("private_key: " + utility.bytes_to_hex_string(self.private_key))
        print("public_key: " + utility.bytes_to_hex_string(self.public_key))
        print("sign_script: " + utility.bytes_to_hex_string(self.sign_script))
        print("program_hash: " + utility.bytes_to_hex_string(self.program_hash))
        print("address: " + self.address)
        print("iv: " + utility.bytes_to_hex_string(self.iv))
        print("master_key: " + utility.bytes_to_hex_string(self.master_key))

    # def decompress(self, yTilde, xValue, curve):
    #     x_coord = xValue
    #     param_a = P256PARAMA
    #     y_square = x_coord ** 2 % abs(curve.p)
    #     y_square += param_a
    #     y_square = y_square % curve.p
    #     y_square *= x_coord
    #     y_square = y_square % curve.p
    #     y_square += y_square % curve.b
    #     y_square = y_square % curve.p
    #
    #     y_value = self.curve_sqrt(y_square, curve)
    #     y_coord = 0
    #     if (y_value % 2 == 0 and yTilde != 0) or (y_value % 2 == 1 and yTilde != 1):
    #         y_coord = curve.p - y_value
    #     else:
    #         y_coord = y_value
    #     return {"X": x_coord, "Y": y_coord}

    # def curve_sqrt(self, y_square, curve):
    #     p = long_to_bytes(curve._p)
    #     if (p[1] == 1):
    #         tmp1 = curve._p << 2
    #         tmp1 = tmp1 + 1
    #
    #         tmp2 = (y_square ** tmp1) % curve._p
    #         tmp3 = (tmp2 ** 2) % curve._p
    #         if tmp3 == y_square:
    #             return tmp2
    #         return None
    #     q_minus_one = curve._p - 1
    #     legend_exp = q_minus_one >> 1
    #     tmp4 = (y_square ** legend_exp) >> curve._p
    #     if tmp4 == 1:
    #         return None
    #     k = q_minus_one >> 2 << 1
    #     k = k + 1
    #
    #     lucas_param_q = y_square
    #     four_q = lucas_param_q << 2
    #     four_q = four_q % curve._p
    #
    #     while (True):
    #         lucas_param_p = 0
    #         while (True):
    #             tmp5 = 0
    #             lucas_param_p = nb.getPrime(p.bit_length(), randfunc=None)
    #             if lucas_param_p < curve._p:
    #                 tmp5 = lucas_param_p * lucas_param_q
    #                 tmp5 = tmp5 - four_q
    #                 tmp5 = (tmp5 ** legend_exp) % curve._p
    #                 if tmp5 == q_minus_one:
    #                     break
    #         seq = self.fast_lucas_seq(curve._p, lucas_param_p, lucas_param_q, k)
    #         seq_u = seq["uh"]
    #         seq_v = seq["vl"]
    #         tmp6 = seq_v * seq_v
    #         tmp6 = tmp6 % curve._p
    #         if tmp6 == four_q:
    #             if seq_v[0] == 1:
    #                 seq_v = seq_v + curve._p
    #             seq_v >> 1
    #             return seq_v
    #         if seq_u == 1 or seq_u == q_minus_one:
    #             break
    #     return None

    # def fast_lucas_seq(self, curve_p, lucas_param_p, lucas_param_q, k):
    #     n = k.bit_length()
    #     s = self.get_lowest_set_bit(k)
    #     uh = 1
    #     vl = 2
    #     ql = 1
    #     qh = 1
    #     vh = lucas_param_p
    #     tmp = 0
    #
    #     j = n - 1
    #     while (j >= s + 1):
    #         if k[j] == 1:
    #             ql = ql * qh
    #             ql = ql % curve_p
    #
    #             uh = uh * vh
    #             uh = uh % curve_p
    #
    #             vl = vh * vl
    #             tmp = lucas_param_p * ql
    #             vl = vl - tmp
    #             vl = vl % curve_p
    #
    #             vh = vh * vh
    #             tmp = qh << 1
    #             vh = vh - tmp
    #             vh = vh % curve_p
    #         else:
    #             qh = ql
    #             uh = uh * ql
    #             uh = uh - ql
    #             uh = uh % curve_p
    #
    #             vh = vh * vl
    #             tmp = lucas_param_p * ql
    #             vh = vh - tmp
    #             vh = vh % curve_p
    #
    #             vl = vl * vl
    #             tmp = ql << 1
    #             vl = vl - tmp
    #             vl = vl % curve_p
    #     j = j - 1
    #     ql = ql * qh
    #     ql = ql % curve_p
    #     qh = ql * lucas_param_q
    #     qh = qh % curve_p
    #
    #     uh = uh * vl
    #     uh = uh - ql
    #     uh = uh % curve_p
    #
    #     vl = vh * vl
    #     tmp = lucas_param_p * ql
    #     vl = vl - tmp
    #     vl = vl % curve_p
    #
    #     ql = ql * qh
    #     ql = ql % curve_p
    #
    #     for j in range(1, s + 1):
    #         uh = uh * vl
    #         uh = uh * curve_p
    #
    #         vl = vl * vl
    #         tmp = ql << 1
    #         vl = vl - tmp
    #         vl = vl % curve_p
    #
    #         ql = ql * ql
    #         ql = ql % curve_p
    #     return {"uh": uh, "vl": vl}
    #
    # def get_lowest_set_bit(self, k):
    #     i = 0
    #     while (k[i] != 1):
    #         i = i + 1
    #     return i

    """
    def add_account(self):
        return

    def add_address(self, program_hash, redeem_script):
        return
    """


class MultiSignAccount(object):
    def __init__(self, m, name, password, public_keys=list()):
        self.public_keys = public_keys
        self.name = name
        self.password = password
        self.n = len(public_keys)
        self.init_multi(public_keys, m)

    def init_multi(self, public_key_eccs, m):
        signature_redeem_script_byte_list = self.create_multi_redeem_script(m, public_key_eccs)
        program_hash = utility.script_to_program_hash(signature_redeem_script_byte_list)
        signature_redeem_script_bytes = b''
        for b in signature_redeem_script_byte_list:
            signature_redeem_script_bytes = signature_redeem_script_bytes + b
        reversed_program_hash = b''
        for b in bytearray(program_hash):
            reversed_program_hash = bytes([b]) + reversed_program_hash

        self.public_key = get_hex_public_key(public_key_eccs[0].public_key())
        self.sign_script = binascii.hexlify(signature_redeem_script_bytes)
        self.program_hash = binascii.hexlify(reversed_program_hash)
        self.address = utility.program_hash_to_address(program_hash).encode()

    def create_multi_redeem_script(self, m, eccs):
        op_code = bytes([utility.PUSH1 + m - 1])
        buf = list()
        buf.append(op_code)
        for ecc in eccs:
            content = encode_point(True, ecc.public_key())
            buf.append(bytes([len(content)]))
        for i in range(len(content)):
            buf.append(bytes([content[i]]))
        n = len(eccs)
        op_code = bytes([utility.PUSH1 + n - 1])
        buf.append(op_code)
        buf.append(bytes([MULTISIG]))
        return buf


def get_hex_public_key(ECCkey):
    encoded = encode_point(is_compressed=True, public_key_ECC=ECCkey)
    hex_value = binascii.hexlify(bytearray(encoded))
    return hex_value


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
    return encodedData
