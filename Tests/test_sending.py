import threading
import time
from collections import deque
from unittest import TestCase

from Client import Client
from Models.Node import Node
from Models.User import User
from RoutingTable import RoutingTable
from Server import Server


class TestSending(TestCase):
    def setUp(self):
        self.command_queues = []
        self.client_threads = []
        self.server_threads = []
        self.locks = []
        self.users = []
        self.tables = []
        self.bucket_limit = 20
        self.lookup_count = 10
        self.bootstrap_node = Node("d4b90f2dfafc736205a98bf3ae6541431bc77d8e", "127.0.0.1", 5555)
        self._generate_n_sets(2)

    def test_user2_to_user1(self):
        self.command_queues[1].append(f"{self.users[0].node.id}:somemsg")
        user1_messages = self.server_threads[0].messages
        time.sleep(2)
        self.assertTrue(len(user1_messages) != 0)
        
    def _generate_n_sets(self, n):
        default_port = 5555
        for i in range(0, n):
            self.users.append(User(f"login{i}", "127.0.0.1", default_port + i))
            self.locks.append(threading.Lock())
            self.tables.append(RoutingTable(self.users[i].node, self.bootstrap_node, self.bucket_limit, f"nodes{i}.txt", self.locks[i]))

            self.server_threads.append(Server(self.users[i].node, self.tables[i], self.lookup_count))
            self.server_threads[i].start()

            self.command_queues.append(deque())
            self.client_threads.append(Client(self.users[i].node, self.tables[i], self.command_queues[i], self.lookup_count))
            self.client_threads[i].start()