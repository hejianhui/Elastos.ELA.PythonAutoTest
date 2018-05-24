'''
Created on Apr 11, 2018

@author: bopeng
'''
import requests
import json
from JsonRPCTests import JsonRPCAPI

class JsonRPCWalletAPI(JsonRPCAPI):
    def __init__(self, config_path='./cli-config.json'):
        self.read_config_file(config_path)

    def read_config_file(self, config_path = './cli-config.json'):
        self.config_path = config_path
        with open(self.config_path) as json_data:
            data = json.load(json_data)
            
            self.url = data["IpAddress"]
            self.port = data['HttpJsonPort']

        self.addr = "http://" + self.url + ":" + self.port