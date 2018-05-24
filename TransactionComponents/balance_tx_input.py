"""
Created on Apr 20, 2018

@author: bopeng
"""


class BalanceTxInput(object):
    """
    classdocs
    """

    def __init__(self, asset_id=b'', value=b'', program_hash=b''):
        """
        Constructor
        """
        self.asset_id = asset_id
        self.value = value
        self.program_hash = program_hash
