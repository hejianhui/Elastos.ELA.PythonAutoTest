"""
Created on Apr 16, 2018

@author: bopeng
"""


class Asset(object):
    """
    classdocs
    """

    def __init__(self, name="", description="", precision=b'', asset_type=b'', record_type=b'\x00'):
        '''
        Constructor
        '''
        self.name = name
        self.description = description
        self.precision = precision
        self.asset_type = asset_type
        self.record_type = record_type

    def serialize(self):
        serialized = b''

        name_length = len(self.name)
        name_length_bytes = bytes([name_length])
        serialized += name_length_bytes
        name_bytes = self.name.encode(encoding='utf_8', errors='strict')
        serialized += name_bytes

        desc_length = len(self.description)
        serialized += bytes([desc_length])
        serialized += self.description.encode()

        serialized += self.precision

        serialized += self.asset_type

        serialized += self.record_type

        return serialized
