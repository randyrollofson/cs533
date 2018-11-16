# Consumer

import socket
import pickle
from threading import Thread
from _thread import *
import time
import random


class Server(Thread):
    queue = []

    def thread2(self, c):
        while True:
            print("thread 2")
            if len(self.queue) > 0:
                num = self.queue.pop(0)
                print("Consumed", num)
                print("Thread 2 sending queue: ", str(self.queue))
                data = pickle.dumps(self.queue)
                c.send(data)
                time.sleep(random.random())
            else:
                print("waiting on producer")

        c.close()

    def thread1(self):
        host = "127.0.0.1"
        port = 12345

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))

        print("socket bound to port", port)
        s.listen(5)

        c, addr = s.accept()

        start_new_thread(self.thread2, (c,))

        while True:
            print("thread 1")
            recvd_data = c.recv(1024)
            self.queue = pickle.loads(recvd_data)
            print('Received from the client :', str(self.queue))
            time.sleep(random.random())

        c.close()
        s.close()


server = Server()
server.thread1()
