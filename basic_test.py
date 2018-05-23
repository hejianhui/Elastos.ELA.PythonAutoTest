#!/usr/bin/env python
# encoding: utf-8

"""
@author: Bocheng.Zhang
@license: Apache Licence 
@contact: bocheng0000@gmail.com
@file: basic_test.py
@time: 2018/5/19 15:19
"""

import sys
import time

import config
from Utility import util
from Utility import node


def func():
    pass


class Main():
    def __init__(self):
        pass


if __name__ == '__main__':
    node_num = 4
    exchange_node_num = 1
    # test_path = '~/dev/work/test'
    test_path = '/Users/bocheng/Desktop'

    # Deploy full node
    test_dir = util.deploy(node_num, test_path, spv=False)

    # Deploy exchange node
    util.deploy(exchange_node_num, test_dir, spv=True)
    print("Deploy finished %s" % test_dir)

    nodes = {}
    spv = {}

    # Modify Node config.json
    # Full Node
    for i in range(node_num):
        _config = {}
        _config['Magic'] = 2018000
        _config['FoundationAddress'] = 'ENUufMgzaPYSPG14HRsT7JviEY7DA7rhAc'

        _config['SeedList'] = ["127.0.0.1:10338", "127.0.0.1:11338", "127.0.0.1:12338", "127.0.0.1:13338"]

        _config['HttpInfoPort'] = util.info_port(i)
        _config['HttpRestPort'] = util.rest_port(i)
        _config['HttpWsPort'] = util.ws_port(i)
        _config['HttpJsonPort'] = util.rpc_port(i)
        _config['NodePort'] = util.p2p_port(i)
        _config['MultiCoreNum'] = 1
        _config['IsTLS'] = True
        _config['CertPath'] = './cert.pem'
        _config['KeyPath'] = './cert-key.pem'
        _config['CAPath'] = './ca.pem'

        if i == 0:
            _config['SPVService'] = True
        else:
            _config['SPVService'] = False

        _pow_config = {}
        _pow_config['MiningSelfPort'] = util.mining_port(i)
        _pow_config['TestNet'] = True
        _pow_config['ActiveNet'] = 'RegNet'
        _pow_config['PayToAddr'] = 'EV2aw69HuF27z2prUDQcGxf4i1rNopwbzj'
        _pow_config['AutoMining'] = False

        _config['PowConfiguration'] = _pow_config

        nodes[i] = node.Node(i, test_dir, host={}, timewait=60, binary=config.node_name, stderr=None, spv=False,
                             extra_conf=_config)

    # Exchange Node
    for i in range(exchange_node_num):
        _config = {}
        _config['Magic'] = 2018000
        _config['FoundationAddress'] = 'ENUufMgzaPYSPG14HRsT7JviEY7DA7rhAc'

        _config['SeedList'] = ["127.0.0.1:20866"]

        _config['HttpInfoPort'] = util.info_port(i, spv=True)
        _config['HttpRestPort'] = util.rest_port(i, spv=True)
        _config['HttpWsPort'] = util.ws_port(i, spv=True)
        _config['HttpJsonPort'] = util.rpc_port(i, spv=True)
        _config['NodePort'] = util.p2p_port(i, spv=True)
        _config['MultiCoreNum'] = 1

        if i == 0:
            _config['SPVService'] = True
        else:
            _config['SPVService'] = False

        _pow_config = {}
        _pow_config['MiningSelfPort'] = util.mining_port(i, spv=True)
        _pow_config['TestNet'] = False
        _pow_config['ActiveNet'] = 'MainNet'
        _pow_config['PayToAddr'] = 'EYW1ykz2EUku6Pv4RqjVLVQQYVfewShcNo'
        _pow_config['AutoMining'] = False

        _config['PowConfiguration'] = _pow_config

        spv[i] = node.Node(i, test_dir, host={}, timewait=60, binary=config.node_name, stderr=None, spv=True,
                           extra_conf=_config)
    # print(nodes)
    #
    # # 启动节点
    # print('Nodes Start')
    # for i in range(node_num):
    #     nodes[i].start()
    #
    # # 等待节点启动完毕，启动RPC服务
    # time.sleep(5)
    # print("Balance of ETpnAkGNPhkUdatGNbRzC78mHG8jWpb3St is ", nodes[0].get_balance(
    #     "ETpnAkGNPhkUdatGNbRzC78mHG8jWpb3St"))
    #
    # print(nodes[0].generate(2))
    # print(nodes[1].generate(3))
    # print(nodes[2].generate(2))
    # print(nodes[3].generate(3))
    #
    # # 当节点高度达到预定高度，设置停止自动挖矿
    # # while True:
    # #     block_count = nodes[1].get_block_count()
    # #     print(nodes[1].url, block_count)
    # #     if block_count >= 10:
    # #         for i in range(node_num):
    # #             nodes[i].set_mining(False)
    # #             print("Node%d's Height is %d" % (i, nodes[i].get_block_count()))
    # #     break
    #
    # # 等待节点同步
    # util.sync_blocks(nodes)
    #
    # for i in range(node_num):
    #     print('Node%d Height:%d NbrCount:%d' % (i, nodes[i].get_block_count() - 1, nodes[i].get_connection_count()))
    #
    # # 关闭后2个节点后，修改其Magic，使其与其他节点隔离
    # print("Update Node3&4 Magic")
    # _config2 = {
    #     "Magic": 2018001
    # }
    # for i in range(2, node_num):
    #     while not nodes[i].is_node_stopped():
    #         nodes[i].stop()
    #         if nodes[i].is_node_stopped():
    #             util.update_config(nodes[i].datadir, _config2)
    #
    # # 启动后2个节点
    # print("Start Node3&4")
    # for i in range(2, node_num):
    #     nodes[i].start()
    #
    # # 检查每个节点的邻居节点数量
    # time.sleep(5)
    # for i in range(node_num):
    #     print("Node%d NbrCount:%s" % (i, nodes[i].get_connection_count()))
    #
    # # 两组节点分别挖矿7个区块与5个区块
    # hash1 = nodes[1].generate(7)
    # hash2 = nodes[3].generate(5)
    #
    # # 打印2组节点区块Hash
    # print(hash1)
    # print(hash2)
    #
    # # 再次检查2组节点邻居节点数量及区块数量
    # for i in range(node_num):
    #     print('Node%d Height:%d NbrCount:%d' % (i, nodes[i].get_block_count() - 1, nodes[i].get_connection_count()))
    #
    # # 关闭后2个节点后，修改其Magic，取消节点隔离
    # print("Stop node3&4 and set the same magic")
    # _config3 = {
    #     "Magic": 2018000
    # }
    # for i in range(2, node_num):
    #     while not nodes[i].is_node_stopped():
    #         nodes[i].stop()
    #         if nodes[i].is_node_stopped():
    #             util.update_config(nodes[i].datadir, _config3)
    #
    # # 启动后2个节点
    # print("Start Node3&4")
    # for i in range(2, node_num):
    #     nodes[i].start()
    #
    # time.sleep(5)  # 等待节点启动完毕
    # for i in range(node_num):
    #     print("Node%d Height:%d BestBlockHash:%s" % (
    #         i, nodes[i].get_block_count() - 1, nodes[i].get_best_block_hash()))
    #
    # nodes[0].generate(3)
    # # 等待节点同步
    # util.sync_blocks(nodes)
    #
    # for i in range(node_num):
    #     print("Node%d Height:%d BestBlockHash:%s" % (
    #         i, nodes[i].get_block_count() - 1, nodes[i].get_best_block_hash()))
    #
    # blockhash = nodes[3].generate(3)
    # print("The 3 Block Hashs are", blockhash)
    #
    # for i in range(node_num):
    #     print("Node%d Height:%d BestBlockHash:%s" % (
    #         i, nodes[i].get_block_count() - 1, nodes[i].get_best_block_hash()))
    #
    # for i in range(node_num):
    #     print(i, nodes[i].running)
    #     nodes[i].stop()
    #     print("Node %d is stoped" % i)
    #     print(i, nodes[i].process)
    #     print(i, nodes[i].is_node_stopped())
    #     time.sleep(5)
