from threading import Thread, Condition
import time
import random

queue = []
MAX_NUM = 5
condition = Condition()
program_duration = 30


class ProducerThread(Thread):
    running = True
    total_wait_time = 0
    total_digits_produced = 0

    def run(self):
        nums = range(5)
        while self.running:
            condition.acquire()
            if len(queue) == MAX_NUM:
                print("Queue full, producer is waiting")
                t0 = time.time()
                condition.wait()
                t1 = time.time()
                self.total_wait_time += (t1 - t0)
                print("Space in queue, Consumer notified the producer")
            num = random.choice(nums)
            queue.append(num)
            self.total_digits_produced += 1
            print("Produced", num)
            print(queue)
            condition.notify()
            condition.release()
            time.sleep(random.random())
            # time.sleep(0.1)


class ConsumerThread(Thread):
    running = True
    total_wait_time = 0
    total_digits_consumed = 0

    def run(self):
        while self.running:
            condition.acquire()
            if not queue:
                print("Nothing in queue, consumer is waiting")
                t0 = time.time()
                condition.wait()
                t1 = time.time()
                self.total_wait_time += (t1 - t0)
                print("Producer added something to queue and notified the consumer")
            num = queue.pop(0)
            self.total_digits_consumed += 1
            print("Consumed", num)
            print(queue)
            condition.notify()
            condition.release()
            time.sleep(random.random())
            # time.sleep(0.1)


p = ProducerThread()
c = ConsumerThread()
p.start()
c.start()
time.sleep(program_duration)
p.running = False
c.running = False

print("Total producer wait time: ", p.total_wait_time)
print("Total consumer wait time: ", c.total_wait_time)
print("Total digits produced:", p.total_digits_produced)
print("Total digits consumed:", c.total_digits_consumed)
