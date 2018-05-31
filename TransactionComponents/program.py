"""
Created on Apr 16, 2018

@author: bopeng
"""

from Utility import utility


class Program(object):
    """
    classdocs
    """

    def __init__(self, code=None, parameter=None):
        """
        Constructor
        """
        self.code = code
        self.parameter = parameter

    def serialize(self, buf):
        extended_para_len = len(self.parameter)
        buf = utility.write_var_unit(buf, extended_para_len)
        buf += self.parameter

        extended_code_len = len(self.code)
        buf = utility.write_var_unit(buf, extended_code_len)
        buf += self.code

        return buf

    def show_info(self):
        print("code:", self.code.hex())
        print('parameter:', self.parameter.hex())
