from multiprocessing import Process
from collections import deque
import csv
from random import randint

import socket
from time import sleep, time
from threading import Thread
import random
import os

# parameter controlling scale model experiment time, in seconds
EXPERIMENT_LENGTH = 60
HOST = "127.0.0.1"

'''
The ModelMachine object initializes both a server-side and client-side connection.
It is initialized with a randomly generated clock rate, and logs all operations
to a csv file.
'''
class ModelMachine:
    def __init__(self, clock_rate, config, directory="logs"):
        self.server_port = config[0]
        self.client_port = config[1]
        self.pid = str(config[2])
        self.clock_rate = clock_rate

        self.msgs = deque([])
        self.server_socket = None
        self.client_socket = None
        self.logical_clock = 0
        self.filename = f"{directory}/pid_{self.pid}_clockrate_{str(self.clock_rate)}.csv"

    # Performs initialization operations to set up a machine
    def init_machine(self):
        # Create csv file
        self.init_log()

        # Initialize connections, sleep to ensure server is set before client connections are accepted
        self.init_server()
        sleep(5)
        self.init_client()

    # Creates CSV file, with filename: "pid_PID_clockrate_CLOCKRATE.csv"
    def init_log(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
        with open(self.filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['logical clock', 'global time', 'event type', 'queue length'])

    # Logs every operation for a machine in a csv file
    def update_log(self, row):
        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)

    # Listens for messages on the server port and appends messages to queue
    def server_messages(self, s):
        conn, addr = s.accept()
        self.server_socket = conn
        print(f"consumer accepted connection {conn} \n")
        while True:
            data = conn.recv(1024)
            data_val = data.decode()
            if data_val == 'shutdown':
                break
            print(f"msg received: {data_val} \n")
            self.msgs.append(data_val)

    # Initializes server-side connection
    def init_server(self):
        port = self.server_port
        print(f"starting server | port val: {port} \n")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, port))
        s.listen()
        # start background thread to listen for server messages
        Thread(target=self.server_messages, args=(s,)).start()

    # Listens for messages on client port and appends messages to queue
    def client_messages(self, client_s):
        while True:
            data = client_s.recv(1024)
            data_val = data.decode()
            if data_val == 'shutdown':
                break
            print(f"msg received: {data_val} \n")
            self.msgs.append(data_val)

    # Initializes client-side connection
    def init_client(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_port = self.client_port
        try:
            client_socket.connect((HOST, client_port))
            print(f"Client-side connection success to port val: {client_port} \n")

        except socket.error as e:
            print(f"Error connecting to port: {client_port} \n {e}")

        self.client_socket = client_socket
        # start background thread to listen for client messages
        Thread(target=self.client_messages, args=(client_socket,)).start()

    # Performs receive, send, and internal operations for a specified period of time
    def perform_ops(self):
        start_time = int(time())
        while (int(time()) - start_time) <= EXPERIMENT_LENGTH:
            sleep(1 / self.clock_rate)
            # if queue is nonempty pop message
            if self.msgs:
                msg = self.msgs.popleft()
                self.logical_clock = max(self.logical_clock, int(msg)) + 1
                event_type = 'receive'
                print(f'{self.pid}: received \n')
            else:
                op = random.randint(1, 10)
                if op <= 3:
                    if op == 1 or op == 3:
                        self.server_socket.sendall(str(self.logical_clock).encode())
                        print(f'{self.pid}: sent \n')
                    if op == 2 or op == 3:
                        self.client_socket.sendall(str(self.logical_clock).encode())
                        print(f'{self.pid}: sent \n')
                    event_type = 'send'

                else:
                    event_type = 'internal'
                    print(f'{self.pid}: internal \n')

                self.logical_clock += 1

            self.update_log([self.logical_clock, int(time()), event_type, len(self.msgs)])

        self.server_socket.sendall('shutdown'.encode())
        self.client_socket.sendall('shutdown'.encode())

        return


# Create a ModelMachine class for each process
def machine(config):
    config.append(os.getpid())
    clock_rate = randint(1, 6)
    model_machine = ModelMachine(clock_rate, config)
    model_machine.init_machine()
    model_machine.perform_ops()
    return


if __name__ == '__main__':
    port1 = 2056
    port2 = 3056
    port3 = 4056

    config1 = [port1, port2]
    p1 = Process(target=machine, args=(config1,))

    config2 = [port2, port3]
    p2 = Process(target=machine, args=(config2,))

    config3 = [port3, port1]
    p3 = Process(target=machine, args=(config3,))

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()
