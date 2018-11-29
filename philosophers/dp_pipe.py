import threading
import random
import time
import os
import errno
from threading import Thread, Lock

lock1 = Lock()
program_duration = 10
philosophers = []

pipe1 = "/tmp/myPipe_11"             # Pipe location
if not os.path.exists(pipe1):       # Create Named Pipe if not exist
    os.mkfifo(pipe1)

pipe2 = "/tmp/myPipe_12"             # Pipe location
if not os.path.exists(pipe2):       # Create Named Pipe if not exist
    os.mkfifo(pipe2)

pipe3 = "/tmp/myPipe_13"             # Pipe location
if not os.path.exists(pipe3):       # Create Named Pipe if not exist
    os.mkfifo(pipe3)

pipe4 = "/tmp/myPipe_14"             # Pipe location
if not os.path.exists(pipe4):       # Create Named Pipe if not exist
    os.mkfifo(pipe4)

pipe5 = "/tmp/myPipe_15"             # Pipe location
if not os.path.exists(pipe5):       # Create Named Pipe if not exist
    os.mkfifo(pipe5)



class Philosopher(Thread):
    running = True
    total_wait_time = 0
    times_eating = 0

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        while self.running:
            self.attempt_to_eat()

    def select_first_chopstick(self):
        if(self.name == 'Philosopher1'):
            pipe = pipe1
        elif(self.name == 'Philosopher2'):
            pipe = pipe2
        elif(self.name == 'Philosopher3'):
            pipe = pipe3
        elif(self.name == 'Philosopher4'):
            pipe = pipe4
        elif(self.name == 'Philosopher5'):
            pipe = pipe5
        return pipe

    def select_second_chopstick(self):
        if(self.name == 'Philosopher1'):
            pipe = pipe2
        elif(self.name == 'Philosopher2'):
            pipe = pipe3
        elif(self.name == 'Philosopher3'):
            pipe = pipe4
        elif(self.name == 'Philosopher4'):
            pipe = pipe5
        elif(self.name == 'Philosopher5'):
            pipe = pipe1
        return pipe        

    def attempt_to_eat(self):
        
        while self.running:
            c1 = self.select_first_chopstick()
            t0 = time.time()
            print(self.name, "is waiting...")
            lock1.acquire()
            fd1 = os.open(c1, os.O_RDWR)
            lock1.release()
            t1 = time.time()
            self.total_wait_time += (t1 - t0)

            try:
                num1 = os.read(fd1,1)            # read from pipe
            except OSError as err:
                if err.errno == errno.EAGAIN or err.errno == errno.EWOULDBLOCK:
                    num1 = None      # Empty Pipe
                else:
                    raise

            if num1 is None:         
                os.close(fd1)
                print(self.name, "failed to pick up chopstick 1")
                # lock1.release()
            else:
                print(self.name, "picks up chopstick 1, attempts to pick up chopstick 2")
                c2 = self.select_second_chopstick()
                # lock2.acquire()
                lock1.acquire()
                fd2 = os.open(c2, os.O_NONBLOCK|os.O_RDWR)
                lock1.release()
                
                try:
                    num2 = os.read(fd2,1)         
                except OSError as err:
                    if err.errno == errno.EAGAIN or err.errno == errno.EWOULDBLOCK:
                        num2 = None      
                    else:
                        raise

                if num2 is None:         
                    print(self.name, "failed to pick up chopstick 2, drops chopstick 1")
                    os.write(fd1,(str(1)).encode())
                    os.close(fd1)
                    os.close(fd2)
                    time.sleep(random.random())
                else:        
                    print(self.name, "has both chopsticks!")   
                    self.eat()
                    os.write(fd1,(str(1)).encode())
                    os.write(fd2,(str(1)).encode())
                    os.close(fd1)
                    os.close(fd2)
                    time.sleep(random.random())

    def eat(self):
        print(self.name, "starts eating")
        self.times_eating += 1
        time.sleep(random.random())
        print(self.name, "finishes eating, drops both chopsticks")


def dining_philosophers():
    f1 = os.open(pipe1, os.O_NONBLOCK|os.O_RDWR)
    os.write(f1,(str(1)).encode())

    f2 = os.open(pipe2, os.O_NONBLOCK|os.O_RDWR)
    os.write(f2,(str(2)).encode())

    f3 = os.open(pipe3, os.O_NONBLOCK|os.O_RDWR)
    os.write(f3,(str(3)).encode())

    f4 = os.open(pipe4, os.O_NONBLOCK|os.O_RDWR)
    os.write(f4,(str(4)).encode())

    f5 = os.open(pipe5, os.O_NONBLOCK|os.O_RDWR)
    os.write(f5,(str(5)).encode())


    philosopher_names = ['Philosopher1', 'Philosopher2', 'Philosopher3', 'Philosopher4', 'Philosopher5']


    philosophers.append(Philosopher(philosopher_names[0]))
    philosophers.append(Philosopher(philosopher_names[1]))
    philosophers.append(Philosopher(philosopher_names[2]))
    philosophers.append(Philosopher(philosopher_names[3]))
    philosophers.append(Philosopher(philosopher_names[4]))


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