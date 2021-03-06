import threading
import time
from collections import deque
from unittest import TestCase
from Helpers import Helper
from Client import Client
from Helpers.NodeExceptions import NodeNotFoundException
from Models.Node import Node
from Models.User import User
from RoutingTable import RoutingTable
from Server import Server


class TestSending(TestCase):
    def setUp(self):
        self.command_queues = []
        self.output_queues = []
        self.client_threads = []
        self.server_threads = []
        self.locks = []
        self.users = []
        self.tables = []
        self.bucket_limit = 20
        self.k = 10
        self.alpha = 3
        self.connections_count = 20
        self.bootstrap_node = Node("bootstrap_node", "127.0.0.1", 5555)
        self.private_nodes_count = 5
        self.public_nodes_count = 2
        self._generate_private_nodes(self.private_nodes_count)
        self._generate_public_nodes(self.public_nodes_count)

    def tearDown(self):
        self._stop_threads()

    # def test_group_chats(self):
    #     public_user = self.users[self.private_nodes_count + 1]
    #     for command_queue in self.command_queues[:self.private_nodes_count]:
    #         command_queue.append(f"{public_user.node.id} SUBSCRIBE 0")
    #
    #     time.sleep(10)
    #     self.command_queues[0].append(f"{public_user.node.id} STORE some_msg")
    #     time.sleep(10)
    #     for thread in self.server_threads[1:self.private_nodes_count]:
    #         self.assertTrue(len(thread.messages) != 0)
    #
    # def test_ping_node(self):
    #     self.assertTrue(Helper.ping_node(self.users[1].node))
    #     unregistered_user = User(f"login{self.private_nodes_count+1}", "127.0.0.1", 5555 + self.private_nodes_count + 1)
    #     self.assertFalse(Helper.ping_node(unregistered_user.node))
    #
    # def test_node_not_found(self):
    #     self.command_queues[1].append(f"some_not_existing_id STORE some_msg")
    #     self.assertRaises(NodeNotFoundException)

    def test_user2_to_user1(self):
        self.command_queues[1].append(f"{self.users[0].node.id} STORE somemsg")
        user1_messages = self.server_threads[0].messages
        time.sleep(5)
        self.assertTrue(len(user1_messages) != 0)

    # def test_2_messages_user2_to_user1(self):
    #     self.command_queues[1].append(f"{self.users[0].node.id} STORE first_msg")
    #     self.command_queues[1].append(f"{self.users[0].node.id} STORE second_msg")
    #     user1_messages = self.server_threads[0].messages
    #     time.sleep(5)
    #     self.assertTrue(len(user1_messages) == 2)

    # def test_messages_from_one_to_many_users(self):
    #     self.command_queues[1].append(f"{self.users[0].node.id} STORE first_msg")
    #     self.command_queues[1].append(f"{self.users[2].node.id} STORE second_msg")
    #     user0_messages = self.server_threads[0].messages
    #     user2_messages = self.server_threads[2].messages
    #     time.sleep(10)
    #     self.assertTrue(len(user0_messages) != 0)
    #     self.assertTrue(len(user2_messages) != 0)
    #
    # def test_messages_many_to_many(self):
    #     self.command_queues[1].append(f"{self.users[0].node.id} STORE first_msg")
    #     self.command_queues[0].append(f"{self.users[2].node.id} STORE second_msg")
    #     user0_messages = self.server_threads[0].messages
    #     user2_messages = self.server_threads[2].messages
    #     time.sleep(10)
    #     self.assertTrue(len(user0_messages) != 0)
    #     self.assertTrue(len(user2_messages) != 0)

    def _generate_private_nodes(self, n):
        default_port = 5555
        for i in range(0, n):
            self.users.append(User(f"private{i}", "127.0.0.1", default_port + i))
            self.locks.append(threading.Lock())
            self.tables.append(RoutingTable(self.users[i].node, self.bootstrap_node, self.bucket_limit, f"nodes{i}.txt",
                                            self.locks[i]))

            self.output_queues.append(deque())
            self.server_threads.append(
                Server(self.users[i].node, self.tables[i], self.output_queues[i], self.k,
                       self.connections_count))
            self.server_threads[i].start()

            self.command_queues.append(deque())
            self.client_threads.append(
                Client(self.users[i].node, self.tables[i], self.command_queues[i], self.k, self.alpha))
            self.client_threads[i].start()

    def _generate_public_nodes(self, n):
        default_port = 5555 + self.private_nodes_count + 1
        for i in range(self.private_nodes_count, self.private_nodes_count + n):
            self.users.append(User(f"public{i}", "127.0.0.1", default_port + i, True))
            self.locks.append(threading.Lock())
            self.tables.append(RoutingTable(self.users[i].node, self.bootstrap_node, self.bucket_limit, f"nodes{i}.txt",
                                            self.locks[i]))

            self.output_queues.append(deque())
            self.server_threads.append(
                Server(self.users[i].node, self.tables[i], self.output_queues[i], self.k,
                       self.connections_count))
            self.server_threads[i].start()

            self.command_queues.append(deque())
            self.client_threads.append(
                Client(self.users[i].node, self.tables[i], self.command_queues[i], self.k, self.alpha))
            self.client_threads[i].start()

    def _stop_threads(self):
        for th in self.server_threads:
            th.stop()
        for th in self.client_threads:
            th.stop()
