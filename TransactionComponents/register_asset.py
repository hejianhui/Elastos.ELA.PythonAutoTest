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

    def __init__(self, asset, amount: int, controller=bytes(21)):
        """
        Constructor
        """
        self.asset = asset
        self.amount = amount
        self.controller = controller

    def serialize(self):
        asset_bytes = self.asset.serialize()
        extended_amount_bytes = self.amount.to_bytes(8, 'little')
        return asset_bytes + extended_amount_bytes + self.controller
