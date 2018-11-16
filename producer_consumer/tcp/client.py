# Producer

import socket
import random
import pickle
from threading import Thread
import time
from _thread import *

MAX_NUM = 5


class Client(Thread):
    queue = []

    def thread2(self, s):
        while True:
            # condition.acquire()
            print("thread 2")
            if len(self.queue) < MAX_NUM:
                nums = range(5)
                num = random.choice(nums)
                self.queue.append(num)
                print("Produced", num)
                print("Thread 2 sending queue: ", str(self.queue))
                data = pickle.dumps(self.queue)
                s.send(data)
                time.sleep(random.random())
            else:
                print("Waiting on consumer")

        s.close()

    def thread1(self):
        host = '127.0.0.1'
        port = 12345

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

        start_new_thread(self.thread2, (s,))

        while True:
            print("thread 1")
            recvd_data = s.recv(1024)
            self.queue = pickle.loads(recvd_data)
            print('Received from the server :', str(self.queue))
            time.sleep(random.random())

        s.close()


client = Client()
client.thread1()
