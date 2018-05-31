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
        print("code2:", self.code)
        code = self.code
        extended_code_len = utility.add_zero(bytes([len(code)]), 1)
        buf = utility.write_var_unit(buf, extended_code_len)
        buf += code

        # print("code:" + utility.bytes_to_hex_string(self.code))
        # print("parameter:" + utility.bytes_to_hex_string(self.parameter))
        return buf

    def show_info(self):
        print("code:", self.code)
        print('parameter:', self.parameter)
