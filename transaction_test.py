from base_class import ELATestFramework
from wallet import wallet
from account import account
from account import multi_sign_account
from utility import utility
from config import logger


class TransactionTest(ELATestFramework):
    def run_test(self):
        account1 = account.Account("foundationwallet1",
                                   "eebfbd55819ea095107b776616669536d9f0bb6d3cd9b21665ea1fb02405cfed")
        account1.show_info()
        account2 = account.Account("foundationwallet2",
                                   "927f1ff719047e0243150447b9c009fc2f17d67fd413beb965b9a9449d42b9b1")
        account2.show_info()
        account3 = account.Account("foundationwallet3",
                                   "8d57d983f5960f6b3b2ed1d4f7350cfa7fb985580eaf4b9a2d8501384ce27369")
        account3.show_info()
        account4 = account.Account("foundationwallet4",
                                   "22e388e026234863ba077fe18783bbf7935c49ed08898995e7f5f64db8d51cef")
        account4.show_info()
        foundation_account = multi_sign_account.MultiSignAccount(3, "name",
                                                                 [account2.ECCkey, account1.ECCkey, account4.ECCkey,
                                                                  account3.ECCkey])
        foundation_account.show_info()

        foundation_wallet = wallet.Wallet(foundation_account)

        wallet1 = wallet.Wallet(account1)
        wallet2 = wallet.Wallet(account2)
        wallet3 = wallet.Wallet(account3)
        wallet4 = wallet.Wallet(account4)
        node0 = self.nodes[0]
        node1 = self.nodes[1]
        node0.start()
        node1.start()
        node0.jsonrpc.wait_for_connection()
        unsigned_transaction = foundation_wallet.create_transaction(foundation_account.address,
                                                                    [account1.address, account2.address], amount=1,
                                                                    fee=1)

        tx = wallet1.sign_multi_transaction(unsigned_transaction)
        tx = wallet2.sign_multi_transaction(tx)
        tx = wallet3.sign_multi_transaction(tx)
        raw_tx = tx.serialize()
        node0.jsonrpc.discretemining(count=110)
        utility.sync_blocks(self.nodes)
        logger.logger.info('send raw transaction result:', node0.jsonrpc.sendrawtransaction(data=raw_tx))
        utility.sync_mempools(self.nodes)

        for node in self.nodes:
            node.stop()


if __name__ == '__main__':
    TransactionTest().main()
