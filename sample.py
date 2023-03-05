import collections
from multiprocessing import Process
from collections import deque
import csv
from random import randint

import socket
from time import sleep, localtime
from threading import Thread
import random
import os


class ModelMachine:
    def __init__(self, clock_rate, config):
        self.config = config
        self.msgs = deque([])
        self.clock_rate = clock_rate
        self.conn = None
        self.client_s = None
        self.logical_clock = 0
        self.filename = 'clock_rate_' + str(round(self.clock_rate, 2)) + '.csv'

        # create csv file
        self.init_log()

        # initialize connections
        self.init_server(config)

    def consumer(self, conn):
        print("consumer accepted connection" + str(conn) + "\n")
        while True:
            data = conn.recv(1024)
            data_val = data.decode('ascii')
            print("msg received:", data_val)
            self.msgs.append(data_val)

    def init_log(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
        with open(self.filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['logical clock', 'global time', 'event type', 'queue length'])

    def update_log(self, row):
        with open(self.filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)

    def init_server(self, config):
        host = str(config[0])
        port = int(config[1])

        # listen server-side
        print("starting server| port val:", port)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen()
        # add delay to initialize the server logic on all processes
        sleep(5)

        conn, addr = s.accept()
        Thread(target=self.consumer, args=(conn,)).start()
        self.conn = conn

    def init_client(self):
        # connect client-side
        client_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_port = self.config[2]
        host = str(self.config[0])
        try:
            client_s.connect((host, client_port))
            print("Client-side connection success to port val:" + str(client_port) + "\n")

        except socket.error as e:
            print("Error connecting producer: %s" % e)

        self.client_s = client_s


    def perform_ops(self):
        while True:
            sleep(self.clock_rate)
            # if queue is nonempty pop message
            if self.msgs:
                msg = self.msgs.popleft()
                self.logical_clock = max(self.logical_clock, int(msg)) + 1
                event_type = 'receive'
                print(str(self.config[3]) + 'received')
            else:
                op = random.randint(1, 10)
                if op <= 3:
                    if op == 1 or op == 3:
                        self.conn.send(str(self.logical_clock))
                    elif op == 2 or op == 3:
                        self.client_s.send(str(self.logical_clock))
                    event_type = 'send'
                    print(str(self.config[3]) + 'sent')
                else:
                    event_type = 'internal'
                    print(str(self.config[3]) + 'internal')

                self.logical_clock += 1

            self.update_log([self.logical_clock, localtime, event_type, len(self.msgs)])


def machine(config):
    config.append(os.getpid())
    clock_rate = 1 / randint(1, 6)
    print(clock_rate)
    model_machine = ModelMachine(clock_rate, config)
    model_machine.perform_ops()


if __name__ == '__main__':
    port1 = 2056
    port2 = 3056
    port3 = 4056
    local_host = "127.0.0.1"

    config1 = [local_host, port1, port2]
    p1 = Process(target=machine, args=(config1,))

    config2 = [local_host, port2, port3]
    p2 = Process(target=machine, args=(config2,))

    config3 = [local_host, port3, port1]
    p3 = Process(target=machine, args=(config3,))

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()
