"""
Created on Apr 16, 2018

@author: bopeng
"""
from Utility import utility
import struct


class Transaction(object):
    """
    classdocs
    """

    def __init__(self, tx_type=None, payload_version=0, payload=None, attributes=None, utxo_inputs=None,
                 balance_inputs=None, outputs=None, locktime=0, programs=None, hash=None):
        self.InvalidTransactionSize = -1
        self.PublicKeyScriptLength = 35
        self.SignatureScriptLength = 65
        self.MinMultiSignCodeLength = 105

        self.STANDARD = 0xac
        self.MULTISIG = 0xae

        self.tx_type = tx_type
        self.payload_version = payload_version
        self.payload = payload
        self.attributes = attributes
        self.utxo_inputs = utxo_inputs
        self.balance_inputs = balance_inputs
        self.outputs = outputs
        self.locktime = locktime
        self.programs = programs
        self.hash = hash

    def hashed(self):
        buf_bytes = b''
        if self.hash is None:
            buf_bytes += self.serialize_unsigned()
            print("buf_bytes" + utility.bytes_to_hex_string(buf_bytes))

            f = utility.to_aes_key(buf_bytes)
            self.hash = f
        return self.hash

    def serialize_unsigned(self):
        buf_bytes = b''
        buf_bytes += self.tx_type
        buf_bytes += bytes([self.payload_version])
        if self.payload is None:
            print("Transaction Payload is None")

        buf_bytes += self.payload.serialize()

        print("payload:" + utility.bytes_to_hex_string(buf_bytes))

        buf_bytes += bytes([len(self.attributes)])
        if len(self.attributes) > 0:
            for tx_attribute in self.attributes:
                buf_bytes += tx_attribute.serialize()

        buf_bytes += bytes([len(self.utxo_inputs)])
        if len(self.utxo_inputs) > 0:
            for utxo_input in self.utxo_inputs:
                buf_bytes += utxo_input.serialize()

        buf_bytes += bytes([len(self.outputs)])
        if len(self.outputs) > 0:
            for output in self.outputs:
                buf_bytes += output.serialize()
        print("lock time: ",self.locktime)
        locktime = struct.pack(">I", self.locktime)
        locktime = utility.add_zero(locktime, 4)
        buf_bytes += utility.reverse_values_bitwise(locktime)
        print("locktime:" + str(self.locktime))
        return buf_bytes

    def get_transaction_type(self):
        code = self.get_transaction_code()
        if code is None:
            return 0
        code_length = len(code)
        if code_length != self.PublicKeyScriptLength * 2 and len(code) < self.MinMultiSignCodeLength * 2:
            print("invalid transaction type. redeem script is not a stadard or multi sign type")
        result = code[len(code) - 2:]
        return result

    def get_transaction_code(self):
        code = self.get_programs()[0].code
        if code is None:
            print("invalid transaction type. redeem script not found")
            return None
        return code

    def get_standard_signer(self):
        code = self.get_transaction_code()
        code_length = len(code)
        if code_length != self.PublicKeyScriptLength * 2 or int('0x' + code[code_length - 2:].decode(),
                                                                16) != self.STANDARD:
            print("invalid standard transaction code, length not match")
            return None
        # code = code[:len(code) - 2]
        script = code[:self.PublicKeyScriptLength * 2]
        script_list = utility.valuebytes_to_valuebytelist(script)
        signer = utility.script_to_program_hash(script_list)
        reverse_signer = b''
        for i in range(int(len(signer))):
            reverse_signer += bytes([signer[len(signer) - i - 1]])
        return reverse_signer

    def get_programs(self):
        return self.programs

    def set_programs(self, programs):
        self.programs = programs

    def serialize(self):
        buf = self.serialize_unsigned()
        lens = len(self.programs)
        print("program length:" + str(lens))
        # extended = struct.pack("<Q", lens)
        extended = bytes([lens])
        buf = utility.write_var_unit(buf, extended)
        if lens > 0:
            for p in self.programs:
                buf = p.serialize(buf)
        return buf

    def get_multi_signer(self):
        scripts = self.get_multi_public_keys()
        signers = []
        for script in scripts:
            script.append(self.STANDARD)
            hash_value = utility.script_to_program_hash(script)
            signers.append(hash_value)
        return signers

    def append_signature(self, signer_index, signed_transaction):
        if len(self.programs) <= 0:
            print("missing transaction program")
        new_sign = []
        new_sign.append(bytes([len(signed_transaction)]))
        new_sign.append(signed_transaction)
        param = self.programs[0].parameter
        if param is None:
            param = []
        else:

            buf = b''
            buf += self.serialize_unsigned()
            '''
            should verify public key and signature here, ignored for now
            i = 0
            public_keys = self.get_multi_public_keys()
            while(i < len(param)):
                sign = param[i:i+self.SignatureScriptLength[1:]]
                public_key = public_keys[signer_index][1:]
                pub_key = decode_point(publicKey)
                i += self.SignatureScriptLength  
            '''
        buf += param
        buf += new_sign
        self.programs[0].parameter = buf
        return

    def get_multi_public_keys(self):
        code = self.get_transaction_code()
        if len(code) < self.MinMultiSignCodeLength or code[len(code) - 1] != self.MULTISIG:
            print("not a valid multi sign transaction code, length not enough")
        code = code[:len(code) - 1]
        code = code[1:]
        code = code[:len(code) - 1]
        if len(code) % (self.PublicKeyScriptLength - 1) != 0:
            print("not a valid multi sign transaction code, length not enough")
        i = 0
        public_keys = []
        while i < len(code):
            script = code[i:i + self.PublicKeyScriptLength - 1]
            i += self.PublicKeyScriptLength - 1
            public_keys.append(script)
        return public_keys
