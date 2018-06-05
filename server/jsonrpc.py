import time
import requests
import json

DEFAULT_TIMEOUT = 15


class JSONRPC(object):

    def __init__(self, url, method=None):
        self.url = url
        self.method = method

    def __getattr__(self, method):
        if method.startswith('__') and method.endswith('__'):
            # Python internal stuff
            raise AttributeError

        url = self.url
        return JSONRPC(url=url, method=method)

    def __call__(self, **kwargs):
        print('method:', self.method)
        postdata = json.dumps({'version': '2.0', 'method': self.method, 'params': kwargs, 'id': 0})
        response = requests.post(self.url, data=postdata, headers={'Content-Type': 'application/json'})
        return response.json()

    def wait_for_connection(self):
        time_out = DEFAULT_TIMEOUT
        while True:
            try:
                result = self.getnodestate()
                print('rpc server started', result)
                break
            except requests.exceptions.ConnectionError:
                print('waiting for json rpc server start...', time_out)
                time.sleep(1)
                time_out -= 1
                if time_out == 0:
                    raise ConnectionRefusedError('wait for json rpc connection time out')
                continue
# rpc_connection = JSONRPC("http://127.0.0.1:20336")
# print(rpc_connection.getinfo("a"))
