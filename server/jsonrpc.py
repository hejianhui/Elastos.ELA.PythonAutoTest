import http.client
import decimal
import json
import logging
import urllib.parse

DEFAULT_TIMEOUT = 30

DEFAULT_PORT = 20336

log = logging.getLogger("ElastosRPC")


class JSONRPCException(Exception):
    def __init__(self, rpc_error):
        parent_args = []
        try:
            parent_args.append(rpc_error['message'])
        except:
            pass
        Exception.__init__(self, *parent_args)
        self.error = rpc_error
        self.code = rpc_error['code'] if 'code' in rpc_error else None
        self.message = rpc_error['message'] if 'message' in rpc_error else None

    def __str__(self):
        return '%d: %s' % (self.code, self.message)

    def __repr__(self):
        return '<%s \'%s\'>' % (self.__class__.__name__, self)


def encode_decimal(o):
    if isinstance(o, decimal.Decimal):
        return float(round(o, 8))
    raise TypeError(repr(o) + " is not JSON serializable")


class JSONRPC(object):
    __id_count = 0

    def __init__(self, service_url, service_name=None, timeout=DEFAULT_TIMEOUT, connection=None):
        self.__service_url = service_url
        self.__service_name = service_name
        self.__url = urllib.parse.urlparse(service_url)
        if self.__url.port is None:
            port = DEFAULT_PORT
        else:
            port = self.__url.port

        self.__timeout = timeout

        if connection:
            # Callables re-use the connection of the original proxy
            self.__conn = connection
        elif self.__url.scheme == 'https':
            self.__conn = http.client.HTTPSConnection(self.__url.hostname, port,
                                                      timeout=timeout)
        else:
            self.__conn = http.client.HTTPConnection(self.__url.hostname, port,
                                                     timeout=timeout)

    def __getattr__(self, method):
        if method.startswith('__') and method.endswith('__'):
            # Python internal stuff
            raise AttributeError
        if self.__service_name is not None:
            method = "%s.%s" % (self.__service_name, method)
        return JSONRPC(self.__service_url, method, self.__timeout, self.__conn)

    def __call__(self, **kwargs):
        JSONRPC.__id_count += 1
        log.debug("-%s-> %s %s" % (JSONRPC.__id_count, self.__service_name,
                                   json.dumps(kwargs, default=encode_decimal)))
        postdata = json.dumps({'version': '2.0',
                               'method': self.__service_name,
                               'params': kwargs,
                               'id': JSONRPC.__id_count}, default=encode_decimal)
        self.__conn.request('POST', self.__url.path, postdata,
                            {'Host': self.__url.hostname,
                             'Content-type': 'application/json'})
        self.__conn.sock.settimeout(self.__timeout)

        response = self._get_response()
        if response.get('error') is not None:
            raise JSONRPCException(response['error'])
        elif 'result' not in response:
            raise JSONRPCException({
                'code': -343, 'message': 'missing JSON-RPC result'})

        return response['result']

    def batch_(self, rpc_calls):
        """Batch RPC call.
           Pass array of arrays: [ [ "method", params... ], ... ]
           Returns array of results.
        """
        batch_data = []
        for rpc_call in rpc_calls:
            JSONRPC.__id_count += 1
            m = rpc_call.pop(0)
            batch_data.append({"jsonrpc": "2.0", "method": m, "params": rpc_call, "id": JSONRPC.__id_count})

        postdata = json.dumps(batch_data, default=encode_decimal)
        log.debug("--> " + postdata)
        self.__conn.request('POST', self.__url.path, postdata,
                            {'Host': self.__url.hostname,
                             'Authorization': self.__auth_header,
                             'Content-type': 'application/json'})
        results = []
        responses = self._get_response()
        if isinstance(responses, (dict,)):
            if ('error' in responses) and (responses['error'] is not None):
                raise JSONRPCException(responses['error'])
            raise JSONRPCException({
                'code': -32700, 'message': 'Parse error'})
        for response in responses:
            if response['error'] is not None:
                raise JSONRPCException(response['error'])
            elif 'result' not in response:
                raise JSONRPCException({
                    'code': -343, 'message': 'missing JSON-RPC result'})
            else:
                results.append(response['result'])
        return results

    def _get_response(self):
        http_response = self.__conn.getresponse()
        if http_response is None:
            raise JSONRPCException({
                'code': -342, 'message': 'missing HTTP response from server'})

        content_type = http_response.getheader('Content-Type')
        if content_type != 'application/json':
            print(http_response.headers)
            raise JSONRPCException({
                'code': -342, 'message': 'non-JSON HTTP response with \'%i %s\' from server' % (
                    http_response.status, http_response.reason)})

        responsedata = http_response.read().decode('utf8')
        response = json.loads(responsedata, parse_float=decimal.Decimal)
        if "error" in response and response["error"] is None:
            log.debug("<-%s- %s" % (response["id"], json.dumps(response["result"], default=encode_decimal)))
        else:
            log.debug("<-- " + responsedata)
        return response

# rpc_connection = JSONRPC("http://127.0.0.1:20336")
# print(rpc_connection.getinfo("a"))
