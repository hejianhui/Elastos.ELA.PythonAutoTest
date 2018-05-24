"""
Created on Apr 16, 2018

@author: bopeng
"""
from Utility import utility
import struct


class UTXOTxInput(object):
    """
    classdocs
    """

    def __init__(self, refer_tx_id="00", refer_tx_output_index=0, sequence=0):
        """
        Constructor
        """
        self.refer_tx_id = refer_tx_id
        self.refer_tx_output_index = refer_tx_output_index
        self.sequence = sequence

    def __len__(self):
        if self.refer_tx_id == "00" and self.refer_tx_output_index == 0 and self.sequence == 0:
            return 0
        else:
            return len(self)

    def serialize(self):
        serialized = b''
        refer_tx_id_bytes = utility.add_zero(utility.valuebytes_to_utfbytes(self.refer_tx_id.encode()), 32)
        serialized += refer_tx_id_bytes

        refer_tx_output_index_bytes = utility.reverse_values_bitwise(
            utility.add_zero(bytes([self.refer_tx_output_index]), 2))
        # refer_tx_output_index_bytes = Utility.add_zero(bytes([self.refer_tx_output_index]), 4)
        serialized += refer_tx_output_index_bytes

        sequence_bytes = utility.reverse_values_bitwise(utility.add_zero(bytes([self.sequence]), 4))
        serialized += sequence_bytes

        print("refer_tx_id: " + str(self.refer_tx_id) + "\n")
        print("refer_tx_output_index: " + str(self.refer_tx_output_index) + "\n")
        print("sequence: " + str(self.sequence) + "\n")
        return serialized
