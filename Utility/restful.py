import requests


class RestfulServer:
    def __init__(self, host='127.0.0.1', port=10334):
        self.url = host + str(port)
        self.port = port
        self.prefix = '/api/v1/'

    def get_connection_count(self):
        return requests.get(self.url + self.prefix + 'node/connectioncount').json()

    def get_block_transactions_by_height(self, height):
        return requests.get(self.url + self.prefix + 'block/transactions/height/' + height).json()

    def get_block_by_height(self, height):
        return requests.get(self.url + self.prefix + 'block/details/height/' + height).json()

    def get_block_by_hash(self, block_hash):
        return requests.get(self.url + self.prefix + 'block/details/hash/' + block_hash).json()

    def get_block_height(self):
        return requests.get(self.url + self.prefix + 'block/height').json()

    def get_block_hash(self, height):
        return requests.get(self.url + self.prefix + 'block/hash/' + height).json()

    def get_transaction(self, txid):
        return requests.get(self.url + self.prefix + 'transaction/hash/' + txid).json()

    def get_asset(self, asset_hash):
        return requests.get(self.url + self.prefix + 'asset/' + asset_hash).json()

    def get_balance_by_addr(self, address):
        return requests.get(self.url + self.prefix + 'asset/balances/' + address).json()

    def get_balance_by_asset(self, address, asset_id):
        return requests.get(self.url + self.prefix + 'asset/balance/' + address + '/' + asset_id).json()

    def get_utxo_by_asset(self, address, asset_id):
        return requests.get(self.url + self.prefix + 'asset/utxo/' + address + '/' + asset_id).json()

    def get_utxo_by_address(self, address):
        return requests.get(self.url + self.prefix + 'asset/utxos/' + address).json()

    def get_transaction_pool(self):
        return requests.get(self.url + self.prefix + 'transactionpool/').json()
