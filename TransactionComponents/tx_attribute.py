"""
Created on Apr 11, 2018

@author: bopeng
"""
# import random
import os
from Utility import utility


class TransactionAttribute(object):
    """
    classdocs
    """

    def __init__(self, usage=b'\x00', data=b'', size=0):
        """
        Constructor
        """
        # byte
        self.usage = usage

        # bytes
        self.data = data

        # int
        self.size = size

    def serialize(self):
        serialized = b''
        serialized += self.usage
        data_length = len(self.data)
        serialized += bytes([data_length])
        serialized += self.data

        return serialized

    def new_tx_nonce_attribute(self):
        ta = TransactionAttribute()
        ta.usage = bytes([0])
        ta.data = os.urandom(128)
        # ta.data = bytes([random.getrandbits(128)])
        ta.size = 0
        return ta
