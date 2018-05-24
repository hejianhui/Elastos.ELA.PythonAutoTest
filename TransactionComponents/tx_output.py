"""
Created on Apr 11, 2018

@author: bopeng
"""
from Utility import utility
import struct


class TransactionOutput(object):
    """
    classdocs
    """

    def __init__(self, asset_id=b'\x00', value=0, output_lock=0, program_hash=b''):
        """
        Constructor
        """
        self.asset_id = asset_id
        self.value = value
        if value == b'!\r )9~u<\xbd\xc5n\x82\x9a\xa1\xc5\xdc:\x1c\xfb\x80\x0c':
            print("!")
        self.output_lock = output_lock
        self.program_hash = program_hash

    def __len__(self):
        if self.asset_id == b'\x00' and self.value == 0 and self.output_lock == 0 and self.program_hash == b'':
            return 0
        else:
            return len(self)

    def serialize(self):
        serialized = b''
        serialized += utility.add_zero(self.asset_id, 32)

        expanded_value = int(self.value * 10 ** 8)

        extended_value_bytes = utility.add_zero(struct.pack(">Q", expanded_value), 8)
        v = struct.unpack(">Q", extended_value_bytes)
        reversed_value_bytes = utility.reverse_values_bitwise(extended_value_bytes)

        serialized += reversed_value_bytes
        # serialized += Utility.reverse_values_bitwise(self.value)
        serialized += utility.reverse_values_bitwise(struct.pack("I", self.output_lock))
        serialized += utility.add_zero(self.program_hash, 21)

        print("asset_ID: " + utility.bytes_to_hex_string(self.asset_id) + "\n")
        print("value: " + str(self.value) + "\n")
        print("lock: " + str(self.output_lock) + "\n")
        print("program_hash: " + utility.bytes_to_hex_string(self.program_hash) + "\n")
        return serialized
