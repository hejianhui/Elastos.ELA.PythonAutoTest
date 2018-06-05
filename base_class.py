import os
import shutil
import json
import config
import datetime
from node import node


class ELATestMetaClass(type):
    def __new__(cls, clsname, bases, dct):
        if not clsname == 'ELATestFramework':
            if not ('run_test' in dct):
                raise TypeError("ELATestFramework subclasses must override 'run_test'")
            if '__init__' in dct or 'main' in dct:
                raise TypeError("ELATestFramework subclasses may not override '__init__' or 'main'")

        return super().__new__(cls, clsname, bases, dct)


class ELATestFramework(metaclass=ELATestMetaClass):

    def __init__(self, config_list=list()):

        if config_list is []:
            raise Exception('config list must not be empty!')

        self.config_list = config_list
        self.nodes = self.set_up_nodes()

    def set_up_nodes(self):
        """
        this function receives a list of dictionary ,
        in which each dictionary is composed of node name and its configuration.
        and configuration is also a dictionary.
        :return: list of node objects
        """

        project_path = os.environ.get('GOPATH') + '/'.join(config.ELA_PATH)
        print("source code path:", project_path)

        node_path = "%s/elastos_test_runner_%s" % ("./test", datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(node_path)
        print("Temp dir is:", node_path)
        nodes_list = []

        for index, item in enumerate(self.config_list):
            name = item['name']
            path = os.path.join(node_path, name + str(index))
            os.makedirs(path)
            shutil.copy(os.path.join(project_path, name), os.path.join(path))
            configuration = item['config']
            with open(path + '/config.json', 'w+') as f:
                f.write(json.dumps(configuration, indent=4))

            nodes_list.append(node.Node(i=index, dirname=node_path, configuration=configuration['Configuration']))

        return nodes_list

    def run_test(self):
        raise NotImplementedError

    def main(self):
        print(1)
        self.run_test()
