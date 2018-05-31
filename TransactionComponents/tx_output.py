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

    def __init__(self, asset_id: bytes, value: float, output_lock: int, program_hash: bytes):
        """
        Constructor
        """
        self.asset_id = asset_id
        self.value = value
        self.output_lock = output_lock
        self.program_hash = program_hash

    def serialize(self):
        serialized = b''
        serialized += self.asset_id

        expanded_value = int(self.value * 10 ** 8)

        # extended_value_bytes = utility.add_zero(struct.pack(">Q", expanded_value), 8)
        # reversed_value_bytes = utility.reverse_values_bitwise(extended_value_bytes)

        serialized += expanded_value.to_bytes(8, 'little')
        # serialized += Utility.reverse_values_bitwise(self.value)
        serialized += utility.reverse_values_bitwise(struct.pack("I", self.output_lock))
        serialized += self.program_hash

        return serialized
