'''
Created on Mar 16, 2018

@author: bopeng
'''

import json
import requests
from wsgiref import headers




class RestfulTests(object):
    '''
    This is a Restful API tester. 
    
    '''
    
    
    def __init__(self):
        self.headers = {"content-type": "application/json"}
        '''
         Constructor
        '''
         
         
    '''---------------------------------------------------------------------------------------
    Users should AutoTestDraft individual method manually. See specific methods for details.
      
    In order to get AutoTestDraft respond information retrieved from the target node, user needs to:
        1. call set_address() with target url and port number
        2. call method with required parameters
    ---------------------------------------------------------------------------------------'''
        
     
    ''' 
    Manually set url and port number for tester
    @url: IP address or URL of the target node. It is a string that should keep in format:
    
        "http://XXX.XXX.XXX.XXX"
             or
        "http://www.abcd.efg"
        
    @port: Port number of the target node. It is a string or an integer, the same as the "HttpJsonPort" in "config.json" under target node.
    '''
    def set_address(self, url, port):
        self.url = url
        self.port = port
        self.addr = self.url + ":" + self.port    
                  
    '''
    Get total number of current connections of the target node
    no parameters needed
    @return: A json format respond, giving the number of connections of the targeted node
    '''
    def get_connection_count(self):
        self.api_path = "/api/v1/node/connectioncount"
        resp = requests.get(self.addr + self.api_path,  headers = self.headers) 
        return resp.json()
        
    '''
    Get specific block with the height given
    @height: Height of the target block that the user requires. A string or an integer.
    @return: A json format respond, giving detailed block information
    '''
    def get_block_by_height(self, height):
        self.api_path = "/api/v1/block/details/height"
        resp = requests.get(self.addr + self.api_path + "/" + height, headers = self.headers) 
        return resp.json()
    
    '''
    Get specific block transactions with the height given
    @height: Height of the target block that the user requires. A string or an integer.
    @return: A json format respond, giving detailed block transaction information
    '''
    def get_block_transactions_by_height(self, height):
        self.api_path = '/api/v1/block/transactions/height'
        resp = requests.get(self.addr + self.api_path + "/" + height, headers = self.headers)
        return resp.json()
    
    '''
    Get specific block transactions with the hash value given
    @hash_value: Hash value of the target block that the user requires. A string is required. e.g. 1fa97fc2a22e2d459903f4706213fc2c1aafe1925f16ad39dc4b842be01649b1
    @return: A json format respond, giving detailed block information
    '''
    def get_block_by_hash(self, hash_value):
        self.api_path = "/api/v1/block/details/hash"
        resp = requests.get(self.addr + self.api_path + "/" + hash_value ,headers = self.headers)
        return resp.json()
    
    '''
    Get the height of the current block
    @return: A json format respond, giving current block height.
    '''
    def get_block_height(self):
        self.api_path = "/api/v1/block/height"
        resp = requests.get(self.addr + self.api_path, headers = self.headers)
        return resp.json()
    
    '''
    Get specific hash value of a block with the height given
    @height: Height of the target block that the user requires. A string or an integer.
    @return: A json format respond, giving hash value of the block with the given height
    '''
    def get_block_hash(self, height):
        self.api_path =  "/api/v1/block/hash"
        resp = requests.get(self.addr + self.api_path + "/" + height, headers = self.headers)
        return resp.json()
    
    '''
    This method seems not get implemented in the API
    @assertid:
    @return: 
    '''
    def get_total_issued(self, assertid):
        self.api_path = "/api/v1/totalissued"
        resp = requests.get(self.addr + self.api_path + "/" + assertid, headers = self.headers)
        return resp.json()
    
    '''
    Get transaction details with the hash value of the transaction given
    @hash_value: Hash value of the specific transaction. A string is required. e.g. 1fa97fc2a22e2d459903f4706213fc2c1aafe1925f16ad39dc4b842be01649b1
    @return: Transaction details in json format
    '''
    def get_transaction(self, hash_value):
        self.api_path = "/api/v1/transaction"
        resp = requests.get(self.addr + self.api_path + "/" + hash_value, headers = self.headers)
        return resp.json()
    
    '''
    Get asset details by giving the hash value of it
    @hash_value: Hash value of the block. A string is required, e.g. 1fa97fc2a22e2d459903f4706213fc2c1aafe1925f16ad39dc4b842be01649b1
    @return: Asset details in json format
    '''
    def get_asset(self, hash_value):
        self.api_path = "/api/v1/asset"
        resp = requests.get(self.addr + self.api_path + "/" + hash_value, headers = self.headers)
        return resp.json()
    
    '''
    Get balance of a specific address
    @address: Address of a specific wallet. A string is required. e.g. EdBHoLbG2CYB7eR3QQYHzexw5vUvVBbz6D
    @return: Balance in json format
    '''
    def get_balance_by_address(self, address):
        self.api_path = "/api/v1/asset/balances"
        resp = requests.get(self.addr + self.api_path + "/" + address, headers = self.headers)
        return resp.json()
    
    '''
    Get specific asset balance of a specific address
    @address: Address of a specific wallet, A string is required. e.g. EdBHoLbG2CYB7eR3QQYHzexw5vUvVBbz6D
    @assetid: ID of the asset. A string is required. e.g. a3d0eaa466df74983b5d7c543de6904f4c9418ead5ffd6d25814234a96db37b0.
    '''
    def get_balance_by_asset(self, address, assetid):
        self.api_path = "/api/v1/asset/balance"
        resp = requests.get(self.addr + self.api_path + "/" + address + "/" + assetid, headers = self.headers)
        return resp.json()
    
    def get_utxo_by_asset(self, address, assetid):
        self.api_path = "/api/v1/asset/utxo"
        resp = requests.get(self.addr + self.api_path + "/" + address + "/" + assetid, headers = self.headers)
        return resp.json()
        
    def get_utxo_by_addr(self, address):
        self.api_path = "/api/v1/asset/utxos"
        resp = requests.get(self.addr + self.api_path + "/" + address, headers = self.headers)
        return resp.json()
    
    '''
    Send the transaction with the file given
    @file_path: file location of the transaction file
    @return: respond information
    '''
    def send_raw_transaction(self, file_path):
        self.api_path = "/api/v1/transaction"
        file_data = open(file_path, 'r', -1)
        raw_transaction = file_data.read()
        raw_data = {"Action": "sendrawtransaction", "Version": "1.0.0", "Type": 2, "Data": raw_transaction}
        resp = requests.get(self.addr + self.api_path, data=json.JSONEncoder().encode(raw_data) , headers = self.headers)
        return resp.json()
    
    
    def get_transaction_pool(self):
        self.api_path = "/api/v1/transactionpool"
        resp = requests.get(self.addr + self.api_path, headers = self.headers)
        return resp.json()
    
    '''
    restart target server
    @return respond information
    '''
    def restart(self):
        self.api_path = "/api/v1/restart"
        resp = requests.get(self.addr + self.api_path, headers = self.headers)
        return resp.json()
        
        
        
        
        
        
        
        
        