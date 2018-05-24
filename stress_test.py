from Utility import account
from Utility import utility
from Wallet import wallet
import time
import requests


def get_block_height():
    resp = requests.get("http://127.0.0.1:20334/api/v1/block/height")
    return resp.json()['Result']


ACCOUNT_COUNT = 2

account0 = account.Account("account0", "elatest")
wallet0 = wallet.Wallet(account0)

account_names = locals()
for i in range(ACCOUNT_COUNT):
    account_names['account%s' % str(i + 1)] = account.Account("account" + str(i), "elatest")

current_block_height = get_block_height()
tx = wallet0.create_transaction(from_address=account0.address, to_addresses=[account1.address, account2.address])
