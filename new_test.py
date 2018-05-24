from Utility import key_generator
from Utility import utility

account1 = key_generator.Account("account1", "elastos")
account1.show_info()

account2 = key_generator.Account("account2", "elastos")
account2.show_info()

nodes = utility.deploy(1)

node1 = nodes[0]
node1.start()
