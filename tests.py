import unittest
import warnings
from main import *
from collections import deque
import os
import csv

DIR = 'test_logs'



class ScaleModelTest(unittest.TestCase):
    # Helper function to remove all files in a directory
    def empty_directory(self, dir):
        for file_name in os.listdir(dir):
            file = f'{dir}/{file_name}'
            if os.path.isfile(file):
                os.remove(file)

    # Helper function to create test directory
    def create_dir(self, dir):
        if os.path.isdir(dir):
            self.empty_directory(dir)
        else:
            os.mkdir(dir)

    def csv_to_list(self, filename):
        rows = []
        with open(filename, 'r', newline='') as f:
            csvreader = csv.reader(f)
            for row in csvreader:
                rows.append(row)
        return rows

    def silence_resource_warning(self):
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

    def init_test_machines(self):
        # Initialize 3 processes
        port1 = 5056
        port2 = 6056
        port3 = 7056

        self.machine_1 = ModelMachine(1, [port1, port2, 1])
        self.machine_2 = ModelMachine(1, [port2, port3, 2])
        self.machine_3 = ModelMachine(1, [port3, port1, 3])

        self.machines = [self.machine_1, self.machine_2, self.machine_3]

        for m in self.machines:
            m.init_server()
        sleep(3)
        for m in self.machines:
            m.init_client()

    def close_machines(self):
        # shutdown clients before servers
        for m in self.machines:
            m.client_socket.sendall('shutdown'.encode())
        sleep(3)
        for m in self.machines:
            m.server_socket.sendall('shutdown'.encode())


    def test_init_log(self):
        self.create_dir(DIR)

        process = ModelMachine(1, ['port1', 'port2', 0], DIR)

        # create file
        process.init_log()

        # check that file exists
        self.assertTrue(os.path.exists(process.filename))

        # update file
        process.update_log(['test', 'test', 'test', 'test'])

        # create another log with same name
        process.init_log()

        # check that there is only one file in the directory
        self.assertEqual(len(os.listdir(DIR)), 1)

        # check that old file has been overwritten
        rows = self.csv_to_list(process.filename)
        self.assertEqual(rows, [['logical clock', 'global time', 'event type', 'queue length']])

        # check that multiple logs can be created
        for i in range(1, 10):
            ModelMachine(1, ['port1', 'port2', i], DIR).init_log()
        self.assertEqual(len(os.listdir(DIR)), 10)

        self.empty_directory(DIR)
        os.rmdir(DIR)

    def test_update_log(self):
        self.create_dir(DIR)
        process = ModelMachine(1, ['port1', 'port2', 0], DIR)
        process.init_log()
        for i in range(100):
            process.update_log([i, i, i, i])

        data = self.csv_to_list(process.filename)[1:]
        expected = [[str(i)]*4 for i in range(100)]

        self.assertEqual(data, expected)

        self.empty_directory(DIR)
        os.rmdir(DIR)

    def test_init_server_client(self):
        # set up test machines
        self.init_test_machines()
        self.silence_resource_warning()

        # check that server ports have been correctly initialized
        self.assertEqual(self.machine_1.server_port, 5056)
        self.assertEqual(self.machine_2.server_port, 6056)
        self.assertEqual(self.machine_3.server_port, 7056)

        # check that client ports have been correctly initialized
        self.assertEqual(self.machine_1.client_port, 6056)
        self.assertEqual(self.machine_2.client_port, 7056)
        self.assertEqual(self.machine_3.client_port, 5056)

        # close test machines
        self.close_machines()

    def test_server_client_messages(self):
        # set up test machine
        self.init_test_machines()
        self.silence_resource_warning()

        # test single message send
        self.machine_1.client_socket.sendall('hello'.encode())
        self.machine_1.server_socket.sendall('goodbye'.encode())
        sleep(1)
        self.assertEqual(self.machine_2.msgs, deque(['hello']))
        self.assertEqual(self.machine_3.msgs, deque(['goodbye']))

        # test multiple message send, sleep to simulate clock cycle
        msgs = deque(['I', 'dont', 'know', 'you', 'bye'])
        for msg in msgs:
            self.machine_3.client_socket.sendall(msg.encode())
            sleep(0.2)

        self.assertEqual(self.machine_1.msgs, deque(['I', 'dont', 'know', 'you', 'bye']))

        # close test machines
        self.close_machines()


if __name__ == '__main__':
    unittest.main()




