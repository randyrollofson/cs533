# Consumer

import socket
import pickle
from threading import Thread, Condition
from _thread import *
import time
import random

condition = Condition()
program_duration = 60


class Server(Thread):
    queue = []
    running = True
    total_wait_time = 0
    total_digits_consumed = 0

    def thread2(self, c):
        while self.running:
            condition.acquire()
            print("thread 2")
            if len(self.queue) == 0:
                print("Queue is empty, waiting on producer")
                t0 = time.time()
                condition.wait()
                t1 = time.time()
                self.total_wait_time += (t1 - t0)
            num = self.queue.pop(0)
            self.total_digits_consumed += 1
            print("Consumed", num)
            condition.release()
            time.sleep(random.random())

        c.close()

    def run(self):
        host = "127.0.0.1"
        port = 12345

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))

        print("socket bound to port", port)
        s.listen(5)

        c, addr = s.accept()

        start_new_thread(self.thread2, (c,))

        while self.running:
            # try:
            condition.acquire()
            print("thread 1")
            try:
                recvd_data = c.recv(1024)
            except OSError:
                print("ending program")
                break
            self.queue = pickle.loads(recvd_data)
            print('Received from the server :', str(self.queue))
            condition.notify()
            condition.release()
            time.sleep(random.random())

            condition.acquire()
            data = pickle.dumps(self.queue)
            print('Sending to the client :', str(self.queue))
            try:
                c.send(data)
            except OSError:
                print("ending program")
                break
            condition.release()
            # except OSError:
            #     print("ending program")

        c.close()
        s.close()


server = Server()
server.start()
time.sleep(program_duration)
server.running = False
print("total consumer wait time: ", server.total_wait_time)
print("Total digits consumed:", server.total_digits_consumed)
