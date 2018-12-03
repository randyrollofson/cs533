from threading import Thread, Condition
import time
import random
import os

FILENAME =  os.path.dirname(os.getcwd())+"/file.txt"

program_duration = 60   #time to execute each program
condition = Condition()
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
            with open(FILENAME, 'r') as fread:
                if(len(fread.readlines()) == 10):
                    print("Nothing more to write, waiting for consumer to read\n")
                    t0 = time.time()
                    condition.wait()
                    t1 = time.time()
                    self.total_wait_time = t1-t0
                    print("Space in file, Consumer notified the producer\n")

            num = random.choice(nums)
            with open(FILENAME, 'a+') as fwrite:
                fwrite.write("%d\r\n" % num)
                self.total_digits_produced += 1

            with open(FILENAME, 'r') as fread:
                print("Producer wrote - %d\n" % num)

            with open(FILENAME, 'r') as fin:
                print("Current file contents after producer produced:-")
                file_content = fin.readlines()
                print(file_content,"\n")

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
            with open(FILENAME, 'r') as fin:
                if(len(fin.readlines()) == 0):
                    print("Nothing in file to read, consumer is waiting\n")
                    t0 = time.time()
                    condition.wait()
                    t1 = time.time()
                    self.total_wait_time += (t1 - t0)
                    print("Producer added something to queue and notified the consumer\n")

            with open(FILENAME, 'r') as fin:
                data = fin.read().splitlines(True)
            with open(FILENAME, 'r') as fin:
                line_1 = fin.readline()
                print("Consumer read -",line_1)

            with open(FILENAME, 'w') as fout:
                fout.writelines(data[1:])
                self.total_digits_consumed += 1
            with open(FILENAME, 'r') as fin:
                print("Current file contents after consumer consumed")
                file_content = fin.readlines()
                print(file_content,"\n")

            condition.notify()
            condition.release()
            time.sleep(random.random())

if os.path.isfile(FILENAME):
    pass    #pass if file exists
else:
    with open(FILENAME, 'w'):
        pass    #creates file as it doens't exist

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


print("\n\nAverage wait time:", sum_wait_time / number_of_runs)
print("Average throughput:", sum_throughput / number_of_runs)


