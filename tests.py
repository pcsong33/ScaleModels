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

    def init_test_machines(self, logs=False, cr=False):
        # Initialize 3 processes
        port1 = 5056
        port2 = 6056
        port3 = 7056

        cr1 = cr2 = cr3 = 1
        if cr:
            cr2 = 2
            cr3 = 3
        self.machine_1 = ModelMachine(cr1, [port1, port2, 1], DIR)
        self.machine_2 = ModelMachine(cr2, [port2, port3, 2], DIR)
        self.machine_3 = ModelMachine(cr3, [port3, port1, 3], DIR)

        self.machines = [self.machine_1, self.machine_2, self.machine_3]

        for m in self.machines:
            if logs:
                m.init_log()
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

        # check that server sockets have been created
        self.assertIsNotNone(self.machine_1.server_socket)
        self.assertIsNotNone(self.machine_2.server_socket)
        self.assertIsNotNone(self.machine_3.server_socket)

        # check that client sockets have been created
        self.assertIsNotNone(self.machine_1.client_socket)
        self.assertIsNotNone(self.machine_2.client_socket)
        self.assertIsNotNone(self.machine_3.client_socket)

        # close test machines
        self.close_machines()

    def test_server_client_messages(self):
        # set up test machine
        self.init_test_machines()
        self.silence_resource_warning()

        # ensure message queues are empty on initialization
        self.assertEqual(self.machine_1.msgs, deque([]))
        self.assertEqual(self.machine_2.msgs, deque([]))
        self.assertEqual(self.machine_3.msgs, deque([]))

        # test single message send, sleep for clock cycle
        self.machine_1.client_socket.sendall('hello'.encode())
        sleep(0.2)
        self.machine_1.server_socket.sendall('goodbye'.encode())
        sleep(0.2)
        self.assertEqual(self.machine_2.msgs, deque(['hello']))
        self.assertEqual(self.machine_3.msgs, deque(['goodbye']))

        # test multiple message send, sleep to simulate clock cycle
        msgs = deque(['I', 'dont', 'know', 'you', 'bye'])
        for msg in msgs:
            self.machine_3.client_socket.sendall(msg.encode())
            sleep(0.2)

        self.assertEqual(self.machine_1.msgs, deque(['I', 'dont', 'know', 'you', 'bye']))

        # test sending multiple messages to server socket too
        msgs = deque(['I', 'know', 'you', 'hi'])
        for msg in msgs:
            self.machine_3.server_socket.sendall(msg.encode())
            sleep(0.2)

        self.assertEqual(self.machine_2.msgs, deque(['hello', 'I', 'know', 'you', 'hi']))

        # close test machines
        self.close_machines()

    def test_perform_ops(self):
        self.create_dir(DIR)
        experiment_length = 10

        # set up test machine
        self.init_test_machines(logs=True)
        self.silence_resource_warning()

        for m in self.machines:
            m.perform_ops(experiment_length)

        # assert that each log has roughly experiment_length entries (minus 1 to account for header)
        for m in self.machines:
            length = len(self.csv_to_list(m.filename))
            self.assertAlmostEqual(length, experiment_length + 1, delta=1)

        # close test machines
        self.close_machines()

        # initialize machines with different clock rates
        self.init_test_machines(logs=True, cr=True)

        for m in self.machines:
            m.perform_ops(experiment_length)

        # test that each machine has output csv roughly length experiment length * clock rate
        logs_1 = self.csv_to_list(self.machine_1.filename)[1:]
        logs_2 = self.csv_to_list(self.machine_2.filename)[1:]
        logs_3 = self.csv_to_list(self.machine_3.filename)[1:]

        length_1 = len(logs_1)
        length_2 = len(logs_2)
        length_3 = len(logs_3)

        self.assertAlmostEqual(length_1, experiment_length * 1, delta=1)
        self.assertAlmostEqual(length_2, experiment_length * 2, delta=2)
        self.assertAlmostEqual(length_3, experiment_length * 3, delta=3)

        # test that logs are valid
        prev0 = 0
        prev1 = 0
        for log in logs_1:
            # logical clock should be incrementing by at least 1
            self.assertGreaterEqual(int(log[0]) - prev0, 1)

            # global clock should be incrementing by at least 0
            self.assertGreaterEqual(int(log[1]) - prev1, 0)

            # if queue length > 0, event should be 'receive'
            if int(log[3]) > 0:
                self.assertEquals(log[2], 'receive')

            prev0 = int(log[0])
            prev1 = int(log[1])


        self.empty_directory(DIR)
        os.rmdir(DIR)


if __name__ == '__main__':
    unittest.main()




