"""
Created on Apr 11, 2018

@author: bopeng
"""
from utility import utility
from server import restful
from transactioncomponents import transaction as Tx
from transactioncomponents import register_asset as Ra
from transactioncomponents import tx_attribute as Txa
from transactioncomponents import tx_output as Txo
from transactioncomponents import utxo_tx_input as UTXOi
from transactioncomponents import program as Pg
from transactioncomponents import asset
from transactioncomponents import transfer_asset
import binascii


class Wallet(object):
    """
    classdocs
    """

    def __init__(self, account):
        """
        Constructor
        """

        self.account = account
        self.asset_id = Tx.Transaction(
            tx_type=utility.RegisterAsset,
            payload_version=0,
            payload=Ra.RegisterAsset(
                asset=asset.Asset(
                    name="ELA",
                    precision=bytes([0x08]),
                    asset_type=bytes([0x00])),
                amount=0,
            ),
            attributes=[],
            utxo_inputs=[],
            outputs=[],
            programs=[]
        ).hashed()

        '''
        create_standard_keystore data store in original Go version code, SQLite database should be created 
        temporarily keep data store locally in code
        could export all info into a file contains all wallet information in export_key_info
        it is not recommanded because all data in file are stored without encryption, further changes needed
        '''

    '''
    def create_locked_transaction(self, from_address, to_address, amount, fee, locked_until):
        return self.create_locked_transaction(from_address, to_address, amount, fee, 0)
    
    def create_locked_multioutput_transaction(self, from_address, fee, locked_until, outputs):
        return
    
    def create_multioutput_transaction(self, from_address, fee, outputs):
        return
    '''

    def create_transaction(self, from_address=None, to_addresses=None, amount=0, fee=0, locked_until=0):
        outputs = dict()
        if to_addresses != None and amount != 0:
            for address in to_addresses:
                outputs[address] = amount

        if outputs == None or len(outputs) == 0:
            print("[Wallet], Invalid transaction target")

        # NEED TO SYNC HERE, IGNORED FOR FUTURE IMPLEMENTATION
        print('from address:', from_address)
        spender = utility.address_to_programhash(from_address)
        print("spender:", spender)
        total_output_amount = 0
        tx_outputs = []
        total_output_amount += fee
        for key, value in outputs.items():
            receiver = utility.address_to_programhash(key)
            tx_output = Txo.TransactionOutput(asset_id=self.asset_id, program_hash=receiver, value=value,
                                              output_lock=locked_until)
            total_output_amount += value
            tx_outputs.append(tx_output)

        self.utxos = self.get_utxo_by_address(from_address)[0]
        available_utxos = self.remove_locked_utxos(self.utxos)
        available_utxos.sort(key=lambda x: x['Value'])
        tx_inputs = []
        for utxo in available_utxos:
            utxo_value = float(utxo['Value'])
            utxo_input = UTXOi.UTXOTxInput(
                refer_tx_id=utxo['Txid'],
                refer_tx_output_index=utxo['Index'],
                sequence=100)
            tx_inputs.append(utxo_input)
            if utxo_value < total_output_amount:
                total_output_amount -= utxo_value
            elif utxo_value == total_output_amount:
                total_output_amount = 0
                break
            elif utxo_value > total_output_amount:
                change = Txo.TransactionOutput(
                    asset_id=self.asset_id,
                    value=utxo_value - total_output_amount,
                    output_lock=0,
                    program_hash=spender)
                tx_outputs.append(change)
                total_output_amount = 0
                break
        attributes = []
        tx_attr = Txa.TransactionAttribute().new_tx_nonce_attribute()
        attributes.append(tx_attr)
        tx = Tx.Transaction(
            tx_type=utility.TransferAsset,
            payload=transfer_asset.TransferAsset(),
            attributes=attributes,
            utxo_inputs=tx_inputs,
            outputs=tx_outputs,
            programs=[Pg.Program(code=self.account.sign_script)],
            locktime=0
        )
        return tx

    def sign_standard_transaction(self, transaction):
        buf = b''
        program_hash = transaction.get_standard_signer()
        pgh_a = program_hash
        pgh_b = self.account.program_hash
        if pgh_a != pgh_b:
            return "Invalid signer, program hash not match"

        signed_transaction = utility.do_sign(transaction, self.account.ECCkey)
        buf += bytes([len(signed_transaction)])
        buf += signed_transaction
        code = transaction.get_transaction_code()
        program = Pg.Program(code, buf)
        transaction.set_programs([program])
        return transaction

    def sign_multi_transaction(self, transaction):
        program_hashes = transaction.get_multi_signer()
        pgh_b = self.account.program_hash
        index = 0
        signer_index = -1
        for pgh_a in program_hashes:
            if pgh_a == pgh_b.hex():
                signer_index = index
                break
            index = index + 1
        if signer_index == -1:
            print("Invalid multi sign signer")
            return
        signed_transaction = utility.do_sign(transaction, self.account.ECCkey)
        transaction.append_signature(signed_transaction)
        return transaction

    def get_system_asset_id(self):
        system_token = Tx.Transaction(
            tx_type=utility.RegisterAsset,
            payload_version=0,
            payload=Ra.RegisterAsset(
                asset=asset.Asset(
                    name="ELA",
                    precision=bytes([0x08]),
                    asset_type=bytes([0x00])),
                amount=0,
            ),
            attributes=[],
            utxo_inputs=[],
            outputs=[],
            programs=[]
        )

        asset_id = system_token.hashed()

        print("asset_id: " + binascii.b2a_hex(asset_id).decode())
        return asset_id

    def get_utxo_by_address(self, spender_address):
        utxos = restful.RestfulServer().get_utxo_by_address(spender_address)
        if utxos['Desc'] == 'SUCCESS' or utxos['Desc'] == 'Success':
            return utxos['Result']
        return None

    '''
    Should return the current height of the wallet.
    Since we always assumes the wallet got all required blocks here,
    wallet height should be the same as the server node height.
    '''

    def get_current_height(self):
        height = restful.RestfulServer().get_block_height()['Result']
        return height

    def remove_locked_utxos(self, utxos):
        available_utxos = []
        current_height = self.get_current_height()
        for utxo in utxos['Utxo']:
            # not sure what corresponded sub-category is in utxo json, need to double check
            if 'Locktime' in utxo:
                if utxo['Locktime'] > 0:
                    if utxo['lock_time'] >= current_height:
                        continue
                    utxo['Locktime'] = 0xffffffff - 1
            available_utxos.append(utxo)
        return available_utxos
