from mpi4py import MPI
import random
from threading import Thread, Condition
import time
from _thread import *

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
MAX_NUM = 5
condition = Condition()
program_duration = 30

# Producer
if rank == 1:
    class Producer(Thread):
        queue = []
        running = True
        total_wait_time = 0
        total_digits_produced = 0

        def producer_thread(self):
            while self.running:
                condition.acquire()
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
                print("Producer - Produced: %d" % num)
                condition.release()
                time.sleep(random.random())

        def run(self):
            start_new_thread(self.producer_thread, ())

            while self.running:
                condition.acquire()
                print('Producer - Sending to the Consumer: ' + str(self.queue))
                comm.send(self.queue, dest=0, tag=11)
                condition.release()
                condition.acquire()
                try:
                    self.queue = comm.recv(source=0, tag=11)
                except EOFError:
                    print("ending program")
                    condition.release()
                    break
                print('Producer - Received from the Consumer: ' + str(self.queue))
                condition.notify()
                condition.release()
                time.sleep(random.random())


    producer = Producer()
    producer.start()
    time.sleep(program_duration)
    producer.running = False
    time.sleep(2)
    print("Total producer wait time: %f" % producer.total_wait_time)
    print("Total digits produced: %d" % producer.total_digits_produced)

# Consumer
if rank == 0:
    class Consumer(Thread):
        queue = []
        running = True
        total_wait_time = 0
        total_digits_consumed = 0

        def consumer_thread(self):
            while self.running:
                condition.acquire()
                if len(self.queue) == 0:
                    print("Queue is empty, waiting on producer")
                    t0 = time.time()
                    condition.wait()
                    t1 = time.time()
                    self.total_wait_time += (t1 - t0)
                try:
                    num = self.queue.pop(0)
                except:
                    pass
                self.total_digits_consumed += 1
                print("Consumer - Consumed: %d" % num)
                condition.release()
                time.sleep(random.random())


        def run(self):
            start_new_thread(self.consumer_thread, ())

            while self.running:
                condition.acquire()
                self.queue = comm.recv(source=1, tag=11)
                print('Consumer - Received from Producer: ' + str(self.queue))
                condition.notify()
                condition.release()
                time.sleep(random.random())

                condition.acquire()
                print('Consumer - Sending to Producer: ' + str(self.queue))
                try:
                    comm.send(self.queue, dest=1, tag=11)
                except OSError:
                    print("ending program")
                    condition.release()
                    break
                condition.release()


    consumer = Consumer()
    consumer.start()
    time.sleep(program_duration)
    consumer.running = False
    time.sleep(2)
    print("total consumer wait time: %f" % consumer.total_wait_time)
    print("Total digits consumed: %d" % consumer.total_digits_consumed)
