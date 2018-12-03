
import os
import random
import threading
import time
from threading import Thread
import portalocker

program_duration = 60   #time to execute each program
philosophers = []

sum_wait_time = 0
sum_throughput = 0

class Philosopher(Thread):
    running = True
    total_wait_time = 0
    times_eating = 0

    def __init__(self, name, left_file, right_file):
        threading.Thread.__init__(self)
        self.name = name
        self.left_file = left_file
        self.right_file = right_file

    def run(self):
        while self.running:
            print(self.name, "attempts to write...")
            self.attempt_to_write()

    def attempt_to_write(self):
        left_file = self.left_file
        right_file = self.right_file

        while self.running:
            t0 = time.time()
            print(self.name, "is waiting...")
            file_1 = open(left_file, 'a+')
            portalocker.lock(file_1, portalocker.LOCK_EX)
            t1 = time.time()
            self.total_wait_time += (t1 - t0)
            print(self.name, "has access to",self.left_file[-9:], ", attempts to access", self.right_file[-9:])
            try:
                file_2 = open(right_file, 'a+')
                portalocker.lock(file_2, portalocker.LOCK_EX | portalocker.LOCK_NB)
                print(self.name, "has both files!")
                self.eat(file_2, file_1)
                portalocker.unlock(file_2)
                portalocker.unlock(file_1)
                file_2.close()
                file_1.close()
                time.sleep(random.random())
            except portalocker.exceptions.LockException as exc:
                print(self.name, "failed to access", self.right_file[-9:],"releases", self.left_file[-9:])
                portalocker.unlock(file_1)
                time.sleep(random.random())

    def eat(self, file1, file2):
        print(self.name, "starts writing")
        file1.write(self.name + " wrote at " + time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) +"\n")
        file2.write(self.name + " wrote at " + time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) +"\n")
        self.times_eating += 1
        time.sleep(random.random())
        print(self.name, "finishes writing, releases both files")


def dining_philosophers():
    files = ["file1.txt", "file2.txt", "file3.txt", "file4.txt", "file5.txt"]
    abspath_files = []
    if os.path.isdir(os.path.dirname(os.getcwd())+"/files"):
        pass
    else:
        os.mkdir(os.path.dirname(os.getcwd())+"/files")

    for i in range(len(files)):
        FILENAME = os.path.dirname(os.getcwd())+"/files/" + files[i]
        if os.path.isfile(FILENAME):
            with open(FILENAME, 'w'):
                abspath_files.append(FILENAME)
        else:
            with open(FILENAME, 'w'):
                abspath_files.append(FILENAME)

    philosopher_names = ['Philosopher 1', 'Philosopher 2', 'Philosopher 3', 'Philosopher 4', 'Philosopher 5']


    for i in range(5):
        left_file = abspath_files[i]
        if i == 4:
            right_file = abspath_files[0]
        else:
            right_file = abspath_files[i + 1]
        philosopher = Philosopher(philosopher_names[i], left_file, right_file)
        philosophers.append(philosopher)

    for p in philosophers:
        p.start()
    time.sleep(program_duration)
    Philosopher.running = False
    print("Finishing...")


dining_philosophers()
combined_wait_time = 0
combined_throughput = 0
print("\nWaiting times:")
for philosopher in philosophers:
    combined_wait_time += philosopher.total_wait_time
    print(philosopher.name, ": ", philosopher.total_wait_time)
print("Total wait time:", combined_wait_time)

print("\nNumber of times eating:")
for philosopher in philosophers:
    combined_throughput += philosopher.times_eating
    print(philosopher.name, ": ", philosopher.times_eating)
print("Total throughput:", combined_throughput)



