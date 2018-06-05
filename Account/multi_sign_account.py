from utility import utility


class MultiSignAccount(object):
    def __init__(self, m, name, eccs=list()):
        self.public_keys = eccs
        self.name = name
        self.n = len(eccs)
        self.address = None
        self.program_hash = None
        self.sign_script = None
        self.init_multi(m, eccs)

    def init_multi(self, m, eccs):
        signature_redeem_script_bytes = self.create_multi_redeem_script(m, eccs)
        program_hash = utility.script_to_program_hash(signature_redeem_script_bytes)
        self.sign_script = signature_redeem_script_bytes
        self.program_hash = program_hash
        self.address = utility.program_hash_to_address(program_hash).decode()

    #  structure: (PUSH1 + m -1) | encode_point(public_key) ... | (PUSH1 + n -1) | MULTISIG
    def create_multi_redeem_script(self, m, eccs):
        eccs.sort(key=lambda x: x.public_key().pointQ.x)
        op_code = utility.PUSH1 + m - 1
        buf = b''
        buf += bytes([op_code])
        for ecc in eccs:
            content = utility.encode_point(True, ecc.public_key())
            buf = buf + bytes([len(content)]) + content
        n = len(eccs)
        op_code = utility.PUSH1 + n - 1
        buf += bytes([op_code])
        buf += bytes([utility.MULTISIG])
        return buf

    def show_info(self):
        print("address:", self.address)
        print("program hash:", self.program_hash.hex())
