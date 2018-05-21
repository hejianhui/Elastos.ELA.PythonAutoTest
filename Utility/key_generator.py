"""
Created on Mar 30, 2018

@author: bopeng
"""
from Crypto.Util import number as nb
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
import array
import binascii
import os
import json
from Crypto.Util.number import long_to_bytes

from Utility import utility


class Generator(object):
    """
    classdocs
    """
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

    def __init__(self):

        """
        Constructor
        """
        self.public_key = None
        self.sign_script = None
        self.program_hash = None
        self.address = None
        self.private_key = None
        self.iv = None
        self.master_key = None
        self.name = "./keys.json"

    def to_json(self):
        json_data = {}

        json_data['private_key'] = binascii.b2a_hex(self.private_key).decode("utf-8")
        json_data['public_key'] = self.public_key.decode("utf-8")
        json_data['sign_script'] = self.sign_script.decode("utf-8")
        json_data['program_hash'] = self.program_hash.decode("utf-8")
        json_data['address'] = self.address.decode("utf-8")
        json_data['iv'] = binascii.b2a_hex(self.iv).decode("utf-8")
        json_data['master_key'] = binascii.b2a_hex(self.master_key).decode("utf-8")

        '''
        json_data['private_key'] = self.private_key
        json_data['public_key'] = self.public_key
        json_data['sign_script'] = self.sign_script
        json_data['program_hash'] = self.program_hash
        json_data['address'] =  self.address
        json_data['iv'] = self.iv
        json_data['master_key'] = self.master_key
        '''
        return json_data

    def encode_point(self, is_compressed, public_key_ECC):
        public_key_x = public_key_ECC._point._x
        public_key_y = public_key_ECC._point._y

        if public_key_x is None or public_key_y is None:
            infinity = []
            for i in range(Generator.INFINITYLEN):
                infinity.append(Generator.EMPTYBYTE)
            return infinity
        encodedData = []
        if is_compressed:
            for i in range(Generator.COMPRESSEDLEN):
                encodedData.append(Generator.EMPTYBYTE)
        else:
            for i in range(Generator.NOCOMPRESSEDLEN):
                encodedData.append(Generator.EMPTYBYTE)
            y_bytes = public_key_y.to_bytes()
            for i in range(Generator.NOCOMPRESSEDLEN - len(y_bytes), Generator.NOCOMPRESSEDLEN):
                encodedData[i] = y_bytes[i - Generator.NOCOMPRESSEDLEN + len(y_bytes)]
        x_bytes = public_key_x.to_bytes()
        l = len(x_bytes)
        for i in range(Generator.COMPRESSEDLEN - l, Generator.COMPRESSEDLEN):
            encodedData[i] = x_bytes[i - Generator.COMPRESSEDLEN + l]

        if is_compressed:
            if public_key_y % 2 == 0:
                encodedData[0] = Generator.COMPEVENFLAG
            else:
                encodedData[0] = Generator.COMPODDFLAG
        else:
            encodedData[0] = Generator.NOCOMPRESSEDFLAG
        return encodedData

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

    def decode_point(self, encoded_data):
        if encoded_data[0] == 0x00:
            return {"X": None, "Y": None}
        elif encoded_data[0] == 0x02 or encoded_data[0] == 0x03:
            y_tilde = int(encoded_data[0] & 1)
            print("compressed\n")
            pub_key = self.decompress(y_tilde, encoded_data[self.FLAGLEN: self.FLAGLEN + self.XORYVALUELEN],
                                      self.ECCkey)
            return pub_key
        elif encoded_data[0] == 0x04 or encoded_data[0] == 0x05 or encoded_data[0] == 0x06:
            pub_key_x = encoded_data[self.FLAGLEN: self.FLAGLEN + self.XORYVALUELEN]
            pub_key_y = encoded_data[self.FLAGLEN + self.XORYVALUELEN: self.NOCOMPRESSEDLEN]
            return {"X": pub_key_x, "Y": pub_key_y}
        else:
            print("invalid encode data format")
            return None

    '''
    return a ECC type keypair
    '''

    def create_key_pair(self):
        ECCkey = ECC.generate(curve='P-256')
        self.ECCkey = ECCkey
        return ECCkey

    '''
    return a ECC type keypair with the private key given as hex value
    '''

    def create_public_key_with_private(self, private_key_int):
        ECCkey = ECC.construct(curve='P-256', d=private_key_int)
        self.private_key = ECCkey.d.to_bytes()
        print(ECCkey)
        self.ECCkey = ECCkey
        return ECCkey

    def get_hex_public_key(self, ECCkey):
        encoded = self.encode_point(is_compressed=True, public_key_ECC=ECCkey)
        hex_value = binascii.hexlify(bytearray(encoded))
        return hex_value

    def create_iv(self):
        iv = os.urandom(16)
        self.iv = iv
        '''
        print("iv: " + binascii.b2a_hex(self.iv).decode())
        '''
        return iv

    def create_mastertkey(self):
        master_key = os.urandom(32)
        self.master_key = master_key
        '''
        print("master_key: " + binascii.b2a_hex(self.master_key).decode())
        '''
        return master_key

    def create_multi_key_store(self, m=0, n=0, name="", password=""):
        nm = name
        p = password
        public_key_eccs = []
        for i in range(n):
            name = nm + str(i) + ".json"
            password = p + str(i)
            ECC_path = "./ECC" + str(i) + ".pem"
            self.create_standard_key_store(name, password)
            self.export_key_info(name, ECC_path)
            public_key_eccs.append(self.ECCkey)
        self.init_multi(public_key_eccs, m)

    def create_standard_key_store(self, name, password):
        if not str(name).endswith(".json"):
            name = name + ".json"

        if os.path.isfile(name):
            print("key store file already exist")
            self.import_key_info(key_path=name)
            return

        iv_bytes = self.create_iv()
        master_key_bytes = self.create_mastertkey()
        password_key_bytes = utility.to_aes_key(str.encode(password))
        password_hash = SHA256.new(password_key_bytes)
        password_hash_bytes = password_hash.digest()
        self.password_hash_bytes = password_hash_bytes

        master_key_encrypted_bytes = self.encrypt_master_key(iv_bytes, password_key_bytes, master_key_bytes)
        self.master_key_encrypted_bytes = master_key_encrypted_bytes
        key_pair = self.create_key_pair()

        private_key_int = key_pair._d
        private_key_bytes = private_key_int.to_bytes()
        private_key_byte_array = bytearray(private_key_bytes)
        self.private_key_byte_array = private_key_byte_array
        public_key_ECC = key_pair.public_key()

        '''
        print("private_key_dec:" + str(private_key_dec) + "\n")
        print("private_key_bytes:" + str(private_key_bytes) + "\n")
        print("len_private_key_bytes:" + str(len(private_key_bytes)) + "\n")
        print("private_key_byte_array" + str(private_key_byte_array) + "\n")
        print("public_key_ECC:" + str(public_key_ECC) + "\n")
        '''

        private_key_encrypted_bytes = self.encrypt_private_key(master_key_bytes, private_key_bytes,
                                                               public_key_ECC, iv_bytes)
        self.private_key_encrypted_bytes = private_key_encrypted_bytes
        self.private_key = private_key_bytes
        '''
        print("private_key: " + binascii.b2a_hex(self.private_key).decode())
        '''
        self.init_standard(public_key_ECC)

    def encrypt_master_key(self, iv, password_key, master_key):
        master_key_encrypted = self.aes_encrypt(master_key, password_key, iv)
        return master_key_encrypted

    def encrypt_private_key(self, master_key, private_key, public_key_ECC, iv):

        decrypted_private_key = []
        for i in range(96):
            decrypted_private_key.append(0x00)
        public_key_bytes = self.encode_point(False, public_key_ECC)

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

    def init_multi(self, public_key_eccs, m):
        signature_redeem_script_byte_list = self.create_multi_redeem_script(m, public_key_eccs)
        program_hash = utility.script_to_program_hash(signature_redeem_script_byte_list)
        signature_redeem_script_bytes = b''
        for b in signature_redeem_script_byte_list:
            signature_redeem_script_bytes = signature_redeem_script_bytes + b
        reversed_program_hash = b''
        for b in bytearray(program_hash):
            reversed_program_hash = bytes([b]) + reversed_program_hash

        self.public_key = self.get_hex_public_key(public_key_eccs[0].public_key())
        self.sign_script = binascii.hexlify(signature_redeem_script_bytes)
        self.program_hash = binascii.hexlify(reversed_program_hash)
        self.address = utility.program_hash_to_address(program_hash).encode()

        # print("public_key: " + self.public_key.decode("utf-8"))
        # print("sign_script: " + self.sign_script.decode("utf-8"))
        # print("program_hash: " + self.program_hash.decode("utf-8"))
        # print("address: " + self.address.decode())

    def init_standard(self, public_key_ECC):
        signature_redeem_script_byte_list = self.create_standard_redeem_script(public_key_ECC)
        program_hash = utility.script_to_program_hash(signature_redeem_script_byte_list)
        signature_redeem_script_bytes = b''
        for b in signature_redeem_script_byte_list:
            signature_redeem_script_bytes = signature_redeem_script_bytes + b
        reversed_program_hash = b''
        for b in bytearray(program_hash):
            reversed_program_hash = bytes([b]) + reversed_program_hash

        self.public_key = self.get_hex_public_key(public_key_ECC)
        self.sign_script = binascii.hexlify(signature_redeem_script_bytes)
        self.program_hash = binascii.hexlify(reversed_program_hash)
        self.address = utility.program_hash_to_address(program_hash).encode()

        # print("public_key: " + self.public_key.decode("utf-8"))
        # print("sign_script: " + self.sign_script.decode("utf-8"))
        # print("program_hash: " + self.program_hash.decode("utf-8"))
        # print("address: " + self.address.decode())

    def create_standard_redeem_script(self, public_key_ECC):
        content = self.encode_point(True, public_key_ECC)
        buf = []
        buf.append(bytes([len(content)]))
        for i in range(len(content)):
            buf.append(bytes([content[i]]))
        buf.append(bytes([Generator.STANDARD]))
        return buf

    def create_multi_redeem_script(self, m, eccs):
        op_code = bytes([utility.PUSH1 + m - 1])
        buf = []
        buf.append(op_code)
        for ecc in eccs:
            content = self.encode_point(True, ecc.public_key())
            buf.append(bytes([len(content)]))
        for i in range(len(content)):
            buf.append(bytes([content[i]]))
        n = len(eccs)
        op_code = bytes([utility.PUSH1 + n - 1])
        buf.append(op_code)
        buf.append(bytes([self.MULTISIG]))
        return buf

    def show_info(self):
        '''
        print("private_key: " + binascii.b2a_hex(self.private_key).decode("utf-8"))
        print("public_key: " + self.public_key.decode("utf-8")) 
        print("sign_script: " + self.sign_script.decode("utf-8"))
        print("program_hash: " + self.program_hash.decode("utf-8"))
        print("address: " + self.address.decode("utf-8"))
        print("iv: " + binascii.b2a_hex(self.iv).decode("utf-8"))
        print("master_key: " + binascii.b2a_hex(self.master_key).decode("utf-8"))        
        '''

        print("private_key: " + utility.bytes_to_hex_string(self.private_key))
        print("public_key: " + utility.bytes_to_hex_string(self.public_key))
        print("sign_script: " + utility.bytes_to_hex_string(self.sign_script))
        print("program_hash: " + utility.bytes_to_hex_string(self.program_hash))
        print("address: " + utility.bytes_to_hex_string(self.address))
        print("iv: " + utility.bytes_to_hex_string(self.iv))
        print("master_key: " + utility.bytes_to_hex_string(self.master_key))

    def export_key_info(self, key_path="", ECC_path="./ECC.pem"):
        if key_path == "":
            key_path = self.name
        else:
            self.name = key_path

        if utility.is_file_exist(key_path):
            os.remove(key_path)
        mode = 'w'
        with open(key_path, mode) as f:
            json.dump(self.to_json(), f)

        f = open(ECC_path, 'wt')
        f.write(self.ECCkey.export_key(format='PEM'))
        f.close

    def import_key_info(self, key_path="", ECC_path="./Wallet/ECC.pem"):
        if key_path == "":
            key_path = self.name
        else:
            self.name = key_path
        if utility.is_file_exist(key_path):
            with open(key_path) as json_data:
                data = json.load(json_data)
                self.public_key = data['public_key'].encode("utf-8")
                self.sign_script = data['sign_script'].encode("utf-8")
                self.program_hash = data['program_hash'].encode("utf-8")
                self.address = data['address'].encode("utf-8")
                self.private_key = data['private_key'].encode("utf-8")
                self.iv = data['iv'].encode("utf-8")
                self.master_key = data['master_key'].encode("utf-8")
        f = open(ECC_path, 'rt')
        self.ECCkey = ECC.import_key(f.read())

    def decompress(self, yTilde, xValue, curve):
        x_coord = xValue
        param_a = self.P256PARAMA
        y_square = x_coord ** 2 % abs(curve.p)
        y_square += param_a
        y_square = y_square % curve.p
        y_square *= x_coord
        y_square = y_square % curve.p
        y_square += y_square % curve.b
        y_square = y_square % curve.p

        y_value = self.curve_sqrt(y_square, curve)
        y_coord = 0
        if (y_value % 2 == 0 and yTilde != 0) or (y_value % 2 == 1 and yTilde != 1):
            y_coord = curve.p - y_value
        else:
            y_coord = y_value
        return {"X": x_coord, "Y": y_coord}

    def curve_sqrt(self, y_square, curve):
        p = long_to_bytes(curve._p)
        if (p[1] == 1):
            tmp1 = curve._p << 2
            tmp1 = tmp1 + 1

            tmp2 = (y_square ** tmp1) % curve._p
            tmp3 = (tmp2 ** 2) % curve._p
            if tmp3 == y_square:
                return tmp2
            return None
        q_minus_one = curve._p - 1
        legend_exp = q_minus_one >> 1
        tmp4 = (y_square ** legend_exp) >> curve._p
        if tmp4 == 1:
            return None
        k = q_minus_one >> 2 << 1
        k = k + 1

        lucas_param_q = y_square
        four_q = lucas_param_q << 2
        four_q = four_q % curve._p

        while (True):
            lucas_param_p = 0
            while (True):
                tmp5 = 0
                lucas_param_p = nb.getPrime(p.bit_length(), randfunc=None)
                if lucas_param_p < curve._p:
                    tmp5 = lucas_param_p * lucas_param_q
                    tmp5 = tmp5 - four_q
                    tmp5 = (tmp5 ** legend_exp) % curve._p
                    if tmp5 == q_minus_one:
                        break
            seq = self.fast_lucas_seq(curve._p, lucas_param_p, lucas_param_q, k)
            seq_u = seq["uh"]
            seq_v = seq["vl"]
            tmp6 = seq_v * seq_v
            tmp6 = tmp6 % curve._p
            if tmp6 == four_q:
                if seq_v[0] == 1:
                    seq_v = seq_v + curve._p
                seq_v >> 1
                return seq_v
            if seq_u == 1 or seq_u == q_minus_one:
                break
        return None

    def fast_lucas_seq(self, curve_p, lucas_param_p, lucas_param_q, k):
        n = k.bit_length()
        s = self.get_lowest_set_bit(k)
        uh = 1
        vl = 2
        ql = 1
        qh = 1
        vh = lucas_param_p
        tmp = 0

        j = n - 1
        while (j >= s + 1):
            if k[j] == 1:
                ql = ql * qh
                ql = ql % curve_p

                uh = uh * vh
                uh = uh % curve_p

                vl = vh * vl
                tmp = lucas_param_p * ql
                vl = vl - tmp
                vl = vl % curve_p

                vh = vh * vh
                tmp = qh << 1
                vh = vh - tmp
                vh = vh % curve_p
            else:
                qh = ql
                uh = uh * ql
                uh = uh - ql
                uh = uh % curve_p

                vh = vh * vl
                tmp = lucas_param_p * ql
                vh = vh - tmp
                vh = vh % curve_p

                vl = vl * vl
                tmp = ql << 1
                vl = vl - tmp
                vl = vl % curve_p
        j = j - 1
        ql = ql * qh
        ql = ql % curve_p
        qh = ql * lucas_param_q
        qh = qh % curve_p

        uh = uh * vl
        uh = uh - ql
        uh = uh % curve_p

        vl = vh * vl
        tmp = lucas_param_p * ql
        vl = vl - tmp
        vl = vl % curve_p

        ql = ql * qh
        ql = ql % curve_p

        for j in range(1, s + 1):
            uh = uh * vl
            uh = uh * curve_p

            vl = vl * vl
            tmp = ql << 1
            vl = vl - tmp
            vl = vl % curve_p

            ql = ql * ql
            ql = ql % curve_p
        return {"uh": uh, "vl": vl}

    def get_lowest_set_bit(self, k):
        i = 0
        while (k[i] != 1):
            i = i + 1
        return i

    """
    def add_account(self):
        return

    def add_address(self, program_hash, redeem_script):
        return
    """
