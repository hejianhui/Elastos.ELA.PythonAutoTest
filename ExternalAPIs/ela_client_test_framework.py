'''
Created on Mar 23, 2018

@author: bopeng
'''
import json
import os
import subprocess
import shutil,errno

class ELAClientTest(object):
    '''
    classdocs
    '''

    
    '''
    @config_path path to the config file. If left as empty "", all configuration needs to be passed in by parameters.  
    the configuration file is a json file composed by parameters required by methods to be tested. 
    parameters not required by the testing methods could be left as empty ""
    
    "password": password of the wallet
    "wallet_name": name of the wallet
    "change_password": new password of the wallet
    "client_path": the path for the running environment(path to the ELA wallet client)
    "transaction": a dicitionary composed by parameters required by transactions.
        "from": the address of the source wallet
        "to": the address of the target wallet
        "amount": amount of ELA to be transfered
        "fee": extra fee for the transaction
        "hex_string": hex value of the transaction
        "transaction_file_path": transaction file contains the hex value of the transaction
    "adding_accounts": accounts to be added to create the multi-account wallet, separate by space " "
    "deleted_account": the address of the account to be deleted 
    
    '''
    def __init__(self, config_path = ""):
        '''
        Constructor
        '''
        self.password = ""
        self.wallet_name = ""
        self.change_password = ""
        self.transaction = ""
        self.client_path = "";
        
        self.adding_accounts = ""
        self.deleted_account = ""
        
        if not config_path == "":
            self.read_config_file(config_path)
            self.prepare_client(self.client_path)
        
    '''
    create a new ELA wallet
    @client_path: Path to the running ELA client. If left as "", the value of client_path will be get from configuration file
    @wallet_name Name of the wallet. If left as "", there will be no name for the wallet
    @password: Password of the wallet. If left as "", there will be no password for the wallet
    '''
    
    def create_wallet(self, client_path = "", wallet_name = "", password = ""):

        wallet_name = str(wallet_name)
        password = str(password)
        command_prefix = "./ela-cli wallet"
        
        command = ""
        command = command + command_prefix
        
        if not password == "":
            self.password = password
        if not wallet_name == "":
            self.wallet_name = wallet_name
        if not client_path == "":
            self.client_path = client_path
        
        if self.client_path == "":
            print("[ERROR]No client path assigned.")
            return
        
        if not self.wallet_name == "":
            command = command + " " + "-n " + self.wallet_name
                
        if not self.password == "":
            command = command + " " + "-p " + self.password
        
        command = command + " " + "-c"    
        p = self.execute_command(command)
        p.stdin.write(password + "\n")
        p.stdin.write(password + "\n")
        p.stdin.write(password + "\n")
        p.stdin.flush()
        if not os.path.isfile("./keystore.dat"):
            self.copy_any_thing(self.wallet_name, "./keystore.dat")
        
    '''
    read the configuration file for testing purpose
    @config_path: the path of the configuration file to be loaded
    '''
    def read_config_file(self, config_path = ""):
        if config_path == "":
            return
        self.config_path = config_path
        with open(self.config_path) as json_data:
            data = json.load(json_data)
            
            self.password = data['password']
            self.wallet_name = data['wallet_name']
            self.change_password= data['change_password']
            self.transaction = data['transaction']
            self.client_path = data['client_path']
            self.adding_accounts = data['adding_accounts']
            self.deleted_account = data["deleted_account"]
        
    '''
    get the detailed information of the wallet, including address, public key and program hash
    @password: password of the wallet, 
    '''
    def get_account_info(self, password = ""):
        if password == "":
            password = self.password
        p = self.execute_command("./ela-cli wallet -a")
        p.stdin.write(password + "\n")
        p.stdin.flush()
        
    '''
    change the password of the wallet
    @old_password: previos password of the wallet
    @change_password: new password of the wallet
    '''
    def change_password(self, old_password = "", change_password = ""):
        if old_password == "":
            old_password = self.password
        if change_password == "":
            change_password = self.change_password
        p = self.execute_command("./ela-cli wallet --changepassword")
        p.stdin.write(old_password + "\n")
        p.stdin.write(change_password + "\n")
        p.stdin.write(change_password + "\n")
        p.stdin.flush()
    
    '''
    reset the wallet information
    '''
    def reset(self):
        self.execute_command("./ela-cli wallet --reset")
        
    '''
    add multiple accounts to create a multi-owner wallet
    @accounts: public key of the wallet, separate by space " " if multiple accounts in this parameter
    '''
    def add_accounts(self,  accounts = ""):
        if accounts == "":
            accounts = self.adding_accounts
        self.execute_command("./ela-cli wallet --addaccount " + accounts)
        
    '''
    delete specific account by address
    @delete_account: the address of the deleted account
    '''
    def delete_account(self, deleted_account = ""):
        if deleted_account == "":
            deleted_account = self.deleted_account
        self.execute_command("./ela-cli wallet --deleteaccount " + deleted_account)
    
    '''
    prepate the environment of the client, must be called before any test
    @client_path: the path of the client
    '''
    def prepare_client(self, client_path = ""):
        if not client_path == "":
            self.client_path = client_path
        else:
            return
        print("Client Path: " + self.client_path)
        os.chdir(self.client_path)
    
    '''
    execute shell command
    @command: shell command to be executed
    '''
    def execute_command(self, command):
        print(command)
        return subprocess.Popen([command], stdout = subprocess.PIPE, stdin = subprocess.PIPE, shell = True)
    
    '''
    the automatic procedure of signing and sending transactions when there are multiple owners
    @to_be_signed: the name of the transaction file  to be signed
    @ready_to_send: the name of the transaction file to be send
    @clients_to_sign: paths to clients that required to sign the transaction, seeatate by comma ","
    @passwords_of_clients: password of clients that required to sign the transaction, seperate by comma "," The order corresponds to clients_to_sign
    
    '''
    def multi_sign_send(self, to_be_signed, ready_to_send, clients_to_sign, passwords_of_clients):
        clients = clients_to_sign.split(",")
        passwords = passwords_of_clients.split(",")
        
        if len(clients) > 0:
            current_client = clients[0]
            
            if os.path.exists(ready_to_send):
                self.copy_any_thing(self.client_path + "/" + ready_to_send, current_client + "/" + to_be_signed)
                self.prepare_client(current_client)
                self.sign_transaction(use_file = True, transac = current_client + "/" + to_be_signed , wallet_password = passwords[0])
                    
                if (not clients_to_sign.find(",") == -1 and not passwords_of_clients.find(",") == -1):
                    clients_to_sign = clients_to_sign[clients_to_sign.find(",")+1:]
                    passwords_of_clients = passwords_of_clients[passwords_of_clients.find(",")+1:]
                    self.multi_sign_send(ready_to_send, clients_to_sign, passwords_of_clients)
                else:
                    if not os.path.exists(ready_to_send):
                        self.send_transaction(use_file = True, transac = to_be_signed)
                    else:
                        self.send_transaction(use_file = True, transac = ready_to_send)

                
        else:
            self.send_transaction(use_file = True, transac = ready_to_send)
    
    '''
    create a new transaction to be ready to sign
    @use_file: whether the target has multiple targets or not
    @multi_target_path: the path to the multiple target
    @from_address: current user address
    @to_address: the target address, only useful if there is only one target
    @amount: total amount of ELA to be transfered
    @fee: extra fee for the transaction
    @out_file: file name of the output transaction
    '''
    def create_transaction(self, use_file = False, multi_target_path = "", from_address= "", to_address = "", amount = "", fee = "", out_file = ""):
        from_addr_conf = self.transaction["from"]
        to_addr_conf = self.transaction["to"]
        amount_conf = self.transaction["amount"]
        fee_conf = self.transaction["fee"]

         
        if from_address == "":
            from_address = from_addr_conf
        if to_address == "":
            to_address = to_addr_conf
        if amount == "":
            amount = amount_conf
            
        if str(fee) == "" and not str(fee_conf) == "":
            fee = fee_conf    
        else:
            fee = 0.0001
            
        command = ""
        if use_file:
            command = "./ela-cli wallet -t create --from " + from_address  + " --file " + multi_target_path + " --fee " + str(fee)
        else:
            command = "./ela-cli wallet -t create --from " + from_address  + " --to " + to_address + " --amount " + amount + " --fee " + str(fee)
            
        ##command = command + " >> " + out_file

        lines = self.execute_command(command).stdout.read().split("\n")
        if not out_file == "":
            f = open(out_file, "w")
            for line in lines:
                if len(line) > 1 and "File" not in line and "Multi" not in line:
                    f.write(line)
            f.close()
        
    '''
    method to delete a specific line contains the keyword
    @_file: the path to the target file
    @keyword: a marker to be deleted, will delete the entire line if detected.
    '''
    def delete_line(self, _file, key_word):
        f = open(_file, "r")
        lines = f.readlines()
        f.close()
        f = open(_file, "w")
        for line in lines:
            if not key_word in line:
                f.write(line)
        f.close()
                   
    '''
    sign a created transaction
    @use_file: whether use the file to store the transaction or not
    @transac: if use_file = false, transac is the hex value of the transaction. if use_file = true, transac is the path to the file of the transaction
    @wallet_password: the password of the wallet to sign the transaction
    '''
    def sign_transaction(self, use_file = False, transac = "", wallet_password = ""):
        hex_value = ""
        if use_file:
            if transac == "":
                transac = self.transaction["transaction_file_path"]
            else:
                with open(transac, 'r') as transaction_txn:
                    hex_value = transaction_txn.read().replace('\n', '')
        else:
            if transac == "":
                transac = self.transaction["hex_string"]
            hex_value = transac
        command = "./ela-cli wallet -t sign --hex " + hex_value
        
        p = self.execute_command(command)
        
        if wallet_password == "":
            if not self.password == "":
                p.stdin.write(self.password + "\n")
                p.stdin.flush()
            else:
                p.stdin.write(self.password + "12345679")
                p.stdin.flush()
        else:
            p.stdin.write(wallet_password + "\n")
            p.stdin.flush()
          
    '''
    send the completed transaction to the node
    @use_file: whether use the file to store the transaction or not
    @transac: if use_file = false, transac is the hex value of the transaction. if use_file = true, transac is the path to the file of the transaction
    '''
    def send_transaction(self, use_file = False, transac = ""):
        hex_value = ""
        if use_file:
            if transac == "":
                transac = self.transaction["transaction_file_path"]
            else:
                with open(transac, 'r') as transaction_csv:
                    hex_value = transaction_csv.read().replace('\n', '')
        else:
            if transac == "":
                transac = self.transaction["hex_string"]
            hex_value = transac
        command = "./ela-cli wallet -t send --hex " + hex_value
        self.execute_command(command) 

    '''
    copy a directory or a file from src to dst
    @src: source file or source directory path
    @dst: destination file or destination directory path
    
    '''
    def copy_any_thing(self, src, dst):
        print("----")
        print(src)
        print(dst)
        print("----")
        try:
            shutil.copytree(src, dst)
        except OSError as exc:
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else: raise
    
    '''
    automatically generate wallets with conditions given
    @wallet_count: number of wallet to generate
    @base_wallet_password: password base of each wallet, if base_wallet_password = pwd, the 1st wallet password will be pwd0, the 2nd wallet will be pwd1, and so on
    @base_wallet_name: wallet name of each wallet, if base_wallet_name = testwal, the 1st wallet name  will be testwal0,the 2nd wallet name will be testwal1, and so on
    '''
    def auto_generate_wallets(self, wallet_count = 4, base_wallet_password = "pwd", base_wallet_name = "testwal"):
        base_path = self.client_path
        for i in range(wallet_count):
            curr_pswd = base_wallet_password + str(i);
                
            curr_name = base_wallet_name + str(i) + ".dat"
            ##curr_name = "keystore.dat"
                
            src_path = base_path
            dst_path = base_path + str(i)
            self.copy_any_thing(src_path, dst_path)
            self.prepare_client(dst_path)
            os.remove("keystore.dat")
            os.remove("wallet.db")
            self.create_wallet(wallet_name = curr_name, password = curr_pswd)
                
        self.prepare_client(base_path)
    
    '''
    automatically generate, sign and send transactions with conditions given
    @transaction_config: configuration file path
        "multi_owner" : whether the wallet is owned by multiple people ("True" or "False")
        "multi_target": whether the transaction has multiple targets ("True" or "False")
        "multi_target_path": absolute path to the multiple target path file, e.g.: "/home/bopeng/dev/src/ELAClient/addresses.csv"
        "clients_to_sign" : absolute path to the multiple owner client path, separate by comma "," , e.g.: "/home/bopeng/dev/src/ELAClient3,/home/bopeng/dev/src/ELAClient4"
        "passwords_of_clients": passwords of each client wallets, separate by comma ",", e.g.:  "pwd0,pwd1"
        "from_address": address of the source wallet address, e.g.: "EPX2prPgCC6rKEJQMTJ97WQH5ErWj99JLz"
        "to_address": address of the target wallet address, only use if there is one target
        "amount" : amount of ELA to be trade
        "fee" : amount of extra fee for the transaction
        "to_be_signed" : the name of transaction file to be signed, e.g.;"to_be_signed.txn",
        "ready_to_send" : the name of the transaction file to be send, e.g.:"ready_to_send.txn"
    '''
    def auto_transaction(self, transaction_config = "./transaction_config.json"):
        with open(transaction_config) as json_data:
            data = json.load(json_data)
        self.create_transaction(data["multi_target"], data["multi_target_path"], data["from_address"], data["to_address"], data["amount"], data["fee"], data["to_be_signed"])
        if data["multi_owner"]:
                clients = data["clients_to_sign"].split(",")
                passwords = data["passwords_of_clients"].split(",")
                if not clients[len(clients[0]-1)] == "/":
                    clients[0] = clients[0] + "/"
                if not passwords[len(passwords[0]-1)] == "/":
                    passwords[0] = passwords[0] + "/"                
                self.copy_any_thing(self.client_path + "/" + data["to_be_signed"], clients[0] + data["to_be_signed"])
                self.prepare_client(clients[0])
                self.sign_transaction(use_file = True, transac = clients[0] + data["ready_to_send"] , wallet_password = passwords[0])
                
                clients_to_sign = data["clients_to_sign"][data["clients_to_sign"].find(",")+1:]
                passwords_of_clients = data["passwords_of_clients"][data["passwords_of_clients"].find(",")+1:]
                self.multi_sign_send(data["to_be_signed"], data["ready_to_send"], clients_to_sign, passwords_of_clients)
                
        else:
            self.sign_transaction(True, data["to_be_signed"], data["passwords_of_clients"])
            self.send_transaction(True, data["ready_to_send"])
        
        
        
        
        
        
    
        