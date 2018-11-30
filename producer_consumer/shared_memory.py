from threading import Thread, Condition
import time
import random

queue = []
MAX_NUM = 5
condition = Condition()
program_duration = 60
number_of_runs = 50

sum_wait_time = 0
sum_throughput = 0


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


for i in range(number_of_runs):
    p = ProducerThread()
    c = ConsumerThread()
    p.start()
    c.start()
    time.sleep(program_duration)
    p.running = False
    c.running = False

    sum_wait_time += p.total_wait_time
    sum_wait_time += c.total_wait_time
    sum_throughput += p.total_digits_produced
    sum_throughput += c.total_digits_consumed

    print("\nTotal producer wait time: ", p.total_wait_time)
    print("Total consumer wait time: ", c.total_wait_time)
    print("Total wait time:", p.total_wait_time + c.total_wait_time)
    print("Total digits produced:", p.total_digits_produced)
    print("Total digits consumed:", c.total_digits_consumed)
    print("Total throughput:", p.total_digits_produced + c.total_digits_consumed)

    queue = []

print("\n\nAverage wait time:", sum_wait_time / number_of_runs)
print("Average throughput:", sum_throughput / number_of_runs)
