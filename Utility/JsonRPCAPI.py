'''
Created on Mar 16, 2018
@author: bopeng

Modified on May10, 2018 by Bocheng0000
'''
import requests
import json


class JsonRPCAPI(object):
    '''
    This is a JsonRPC API.
    
    '''

    def __init__(self, node={}):
        '''
        Constructor
        '''
        self.init_node_param(self, node)

    '''    
    It Could read "config.json" in the same directory of this Python file by default or enter your own configuration file path.
    "config.json" is wrote in json format, composed by 5 parts: 
    
        target_url: IP address or URL of the target node
        target_port: Port number of the target node, the same as the "HttpJsonPort" in node's "config.json"
        headers: Headers of current POST request. A dictionary contains "content-type": "application/json" in default
        method: The method name that you want to call from the target node
        params: The Parameters of the method that you want to call from the target node. 
                A dictionary contains all variables {"name1":"value1"...} required by method mentioned above
                Method that do not take parameters require "params" to be an empty dictionaty {}
                
    If such a configuration file do exist and write in correct format, AutoTestDraft could be done by simply call get_respond() without a parameter.
    If not, You should call get_respond() with method name as "method" in 'string' format and parameters as "params" in 'dictionary' format 
        
        OR
        
    You could call specific methods with parameters to AutoTestDraft individual method manually. See specific methods for details.    
    '''

    def init_node_param(self, node={}):
        self.path = node.path
        with open(self.config_path) as json_data:
            data = json.load(json_data)
            self.url = data["target_url"]
            self.password = data['passsword']
            self.port = data['target_port']
            self.method = data['method']
            self.params = data['params']
            self.headers = data['headers']
        self.addr = "http://" + self.url + ":" + self.port

    # Manually set url and port number for tester
    # @url: IP address or URL of the target node
    # @port: Port number of the target node, the same as the "HttpJsonPort" in node's "config.json"
    def set_address(self, url, port):
        self.url = url
        self.port = port
        self.addr = "http://" + self.url + ":" + self.port

    # General method for sending request and fetching respond
    # @method: The method name that you want to call from the target node
    # @params: The Parameters of the method that you want to call from the target node. A dictionary contains all variables required by method mentioned above
    # return respond from target node in json format 

    def get_respond(self, method="", params=""):
        '''
        --- testing purpose ---
        
        print(addr)
        print(self.method)
        print(self.params)
        print(self.headers)
        '''

        if method == "":
            method = self.method

        if params == "":
            params = self.params

        resp = requests.post(self.addr, json={"method": method, "params": params}, headers=self.headers)
        return resp.json()

    # @height: height of a certain block, should be a string
    def get_block_by_height(self, height):
        resp = requests.post(self.addr, json={"method": "getblockbyheight", "params": {"height": height}},
                             headers=self.headers)
        return resp.json()

    # @level: level of a certain block, should be a string
    def set_log_level(self, level):
        resp = requests.post(self.addr, json={"method": "setloglevel", "params": {"level": level}},
                             headers=self.headers)
        return resp.json()

    def get_block_by_hash(self, hash_value):
        resp = requests.post(self.addr, json={"method": "getblockbyhash", "params": {"hash": hash_value}},
                             headers=self.headers)
        return resp.json()

    def get_current_height(self):
        resp = requests.post(self.addr, json={"method": "getcurrentheight", "params": {}}, headers=self.headers)
        return resp.json()

    def get_block_hash(self, height):
        resp = requests.post(self.addr, json={"method": "getblockhash", "params": {"height": height}},
                             headers=self.headers)
        return resp.json()

    def get_connection_count(self):
        resp = requests.post(self.addr, json={"method": "getconnectioncount", "params": {}}, headers=self.headers)
        return resp.json()

    def get_transaction_pool(self):
        resp = requests.post(self.addr, json={"method": "gettransactionpool", "params": {}}, headers=self.headers)
        return resp.json()

    def get_raw_transaction(self, hash_value):
        resp = requests.post(self.addr, json={"method": "getrawtransaction", "params": {"hash": hash_value}},
                             headers=self.headers)
        return resp.json()

    def get_neighbors(self):
        resp = requests.post(self.addr, json={"method": "getneighbors", "params": {}}, headers=self.headers)
        return resp.json()

    def get_nodestate(self):
        resp = requests.post(self.addr, json={"method": "getnodestate", "params": {}}, headers=self.headers)
        return resp.json()

    def send_raw_transaction(self, data):
        resp = requests.post(self.addr, json={"method": "sendrawtransaction", "params": {"Data": data}},
                             headers=self.headers)
        return resp.json()

    def submit_block(self, block):
        resp = requests.post(self.addr, json={"method": "submitblock", "params": {"block": block}},
                             headers=self.headers)
        return resp.json()

    ## mining interfaces
    def get_info(self):
        resp = requests.post(self.addr, json={"method": "getinfo", "params": {}}, headers=self.headers)
        return resp.json()

    def help(self):
        resp = requests.post(self.addr, json={"method": "help", "params": {}}, headers=self.headers)

        return resp.json()

    def submit_aux_block(self, blockhash, auxpow):
        resp = requests.post(self.addr,
                             json={"method": "submitauxblock", "params": {"blockhash": blockhash, "auxpow": auxpow}},
                             headers=self.headers)

        return resp.json()

    def create_aux_block(self, paytoaddress):
        resp = requests.post(self.addr, json={"method": "createauxblock", "params": {"paytoaddress": paytoaddress}},
                             headers=self.headers)
        return resp.json()

    def toggle_mining(self, mining):
        resp = requests.post(self.addr, json={"method": "togglemining", "params": {"mining": mining}},
                             headers=self.headers)
        return resp.json()

    def manual_mining(self, count):
        resp = requests.post(self.addr, json={"method": "manualmining", "params": {"count": count}},
                             headers=self.headers)
        return resp.json()
