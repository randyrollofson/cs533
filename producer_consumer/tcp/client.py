# Producer

import socket
import random
import pickle
from threading import Thread, Condition
import time
from _thread import *

MAX_NUM = 5
condition = Condition()
program_duration = 30


class Client(Thread):
    queue = []
    running = True
    total_wait_time = 0
    total_digits_produced = 0

    def thread2(self, s):
        while self.running:
            condition.acquire()
            print("thread 2")
            if len(self.queue) == MAX_NUM:
                print("Queue is full, waiting on consumer")
                t0 = time.time()
                condition.wait()
                t1 = time.time()
                self.total_wait_time += (t1 - t0)
            nums = range(5)
            num = random.choice(nums)
            self.queue.append(num)
            self.total_digits_produced += 1
            print("Produced", num)
            condition.release()
            time.sleep(random.random())

        s.close()

    def run(self):
        host = '127.0.0.1'
        port = 12345

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

        # Don't want to start with an empty queue
        nums = range(5)
        num = random.choice(nums)
        self.queue.append(num)
        self.total_digits_produced += 1

        start_new_thread(self.thread2, (s,))

        while self.running:
            # try:
            condition.acquire()
            print("thread 1")
            data = pickle.dumps(self.queue)
            print('Sending to the server :', str(self.queue))
            s.send(data)
            condition.release()

            condition.acquire()
            recvd_data = s.recv(1024)
            try:
                self.queue = pickle.loads(recvd_data)
            except EOFError:
                print("ending program")
                condition.release()
                break
            print('Received from the server :', str(self.queue))
            condition.notify()
            condition.release()
            time.sleep(random.random())

        s.close()


client = Client()
client.start()
time.sleep(program_duration)
client.running = False
print("Total producer wait time: ", client.total_wait_time)
print("Total digits produced:", client.total_digits_produced)

