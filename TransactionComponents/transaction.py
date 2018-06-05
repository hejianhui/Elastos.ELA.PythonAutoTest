"""
Created on Apr 16, 2018

@author: bopeng
"""
from utility import utility


class Transaction(object):
    """
    classdocs
    """

    def __init__(self, tx_type=None, payload_version=0, payload=None, attributes=None, utxo_inputs=None,
                 outputs=None, locktime=0, programs=None, hash=None):
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
        self.outputs = outputs
        self.locktime = locktime
        self.programs = programs
        self.hash = hash

    def hashed(self):
        buf_bytes = b''
        if self.hash is None:
            buf_bytes += self.serialize_unsigned()

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

        buf_bytes += bytes([len(self.attributes)])
        if len(self.attributes) > 0:
            for tx_attribute in self.attributes:
                buf_bytes += tx_attribute.serialize()

        buf_bytes += bytes([len(self.utxo_inputs)])
        if len(self.utxo_inputs) > 0:
            for utxo_input in self.utxo_inputs:
                buf_bytes += utxo_input.serialize()

        length = len(self.outputs)
        if length < 255:
            # one byte, 8 bits, 1111 1111
            buf_bytes += length.to_bytes(1, byteorder='little')
        else:
            # two byte, 16 bits, 1111 1111 1111 1111,
            # we do not support 32 bits and 64 bits now.
            buf_bytes += b'\xfd'
            buf_bytes += length.to_bytes(2, byteorder='little')
        if len(self.outputs) > 0:
            for output in self.outputs:
                buf_bytes += output.serialize()

        buf_bytes += self.locktime.to_bytes(4, byteorder='little')
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
        if code_length != self.PublicKeyScriptLength or code[-1] != self.STANDARD:
            print("invalid standard transaction code, length not match")
            return None
        return utility.script_to_program_hash(code)

    def get_programs(self):
        return self.programs

    def set_programs(self, programs):
        self.programs = programs

    def serialize(self):
        buf = self.serialize_unsigned()
        lens = len(self.programs)
        buf = utility.write_var_unit(buf, lens)
        if lens > 0:
            for p in self.programs:
                buf = p.serialize(buf)
        return buf.hex()

    def get_multi_signer(self):
        scripts = self.get_multi_public_keys()
        signers = []
        for script in scripts:
            script += bytes([self.STANDARD])
            hash_value = utility.script_to_program_hash(script)
            signers.append(hash_value.hex())
        return signers

    def append_signature(self, signed_transaction):
        if len(self.programs) <= 0:
            print("missing transaction program")
        new_sign = b''
        new_sign += (bytes([len(signed_transaction)]))
        new_sign += signed_transaction
        if self.programs[0].parameter is None:
            self.programs[0].parameter = b''
        self.programs[0].parameter += new_sign
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
