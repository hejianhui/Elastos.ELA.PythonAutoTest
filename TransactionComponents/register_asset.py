"""
Created on Apr 16, 2018

@author: bopeng
"""
import struct
from Utility import utility


class RegisterAsset(object):
    """
    classdocs
    """

    def __init__(self, asset=None, amount=None, controller=None):
        """
        Constructor
        """
        self.asset = asset
        self.amount = amount
        self.controller = controller

    def serialize(self):
        asset_bytes = self.asset.serialize()

        extended_amount_bytes = utility.add_zero(struct.pack(">Q", self.amount), 8)
        reversed_amount_bytes = utility.reverse_values_bitwise(extended_amount_bytes)

        extended_controller_bytes = utility.add_zero(struct.pack(">Q", self.controller), 21)
        reversed_controller_bytes = utility.reverse_values_bitwise(extended_controller_bytes)

        return asset_bytes + reversed_amount_bytes + reversed_controller_bytes
