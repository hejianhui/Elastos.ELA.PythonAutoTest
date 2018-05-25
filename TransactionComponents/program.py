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
        extended_para_len = utility.add_zero(bytes([len(self.parameter)]), 1)
        buf = utility.write_var_unit(buf, extended_para_len)
        buf += self.parameter

        utf_code = utility.valuebytes_to_utfbytes(self.code)
        extended_code_len = utility.add_zero(bytes([len(utf_code)]), 1)
        buf = utility.write_var_unit(buf, extended_code_len)
        buf += utf_code

        # print("code:" + utility.bytes_to_hex_string(self.code))
        # print("parameter:" + utility.bytes_to_hex_string(self.parameter))
        return buf
