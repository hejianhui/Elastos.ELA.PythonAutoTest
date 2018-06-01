"""
Created on Apr 16, 2018

@author: bopeng
"""


class UTXOTxInput(object):
    """
    classdocs
    """

    def __init__(self, refer_tx_id: str, refer_tx_output_index: int, sequence: int):
        """
        Constructor
        """
        self.refer_tx_id = refer_tx_id
        self.refer_tx_output_index = refer_tx_output_index
        self.sequence = sequence

    def serialize(self):
        serialized = b''
        serialized += bytes.fromhex(self.refer_tx_id)
        serialized += self.refer_tx_output_index.to_bytes(2, "little")  # convert to uint16
        serialized += self.sequence.to_bytes(4, 'little')  # convert to uint32
        return serialized
