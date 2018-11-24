import threading
import random
import time
from threading import Thread, Lock


program_duration = 10
philosophers = []


class Philosopher(Thread):
    running = True
    total_wait_time = 0
    times_eating = 0

    def __init__(self, name, left_chopstick, right_chopstick):
        threading.Thread.__init__(self)
        self.name = name
        self.left_chopstick = left_chopstick
        self.right_chopstick = right_chopstick

    def run(self):
        while self.running:
            print(self.name, "attempts to eat...")
            self.attempt_to_eat()

    def attempt_to_eat(self):
        chopstick1 = self.left_chopstick
        chopstick2 = self.right_chopstick

        while self.running:
            t0 = time.time()
            print(self.name, "is waiting...")
            chopstick1.acquire(True)
            t1 = time.time()
            self.total_wait_time += (t1 - t0)
            print(self.name, "picks up chopstick 1, attempts to pick up chopstick 2")
            chopstick2_attempt = chopstick2.acquire(False)
            if not chopstick2_attempt:
                print(self.name, "failed to pick up chopstick 2, drops chopstick 1")
                chopstick1.release()
                time.sleep(random.random())
            else:
                print(self.name, "has both chopsticks!")
                self.eat()
                chopstick2.release()
                chopstick1.release()
                time.sleep(random.random())

    def eat(self):
        print(self.name, "starts eating")
        self.times_eating += 1
        time.sleep(random.random())
        print(self.name, "finishes eating, drops both chopsticks")


def dining_philosophers():
    chopsticks = []
    for i in range(5):
        chopsticks.append(Lock())

    philosopher_names = ['Philosopher 1', 'Philosopher 2', 'Philosopher 3', 'Philosopher 4', 'Philosopher 5']

    for i in range(5):
        left_chopstick = chopsticks[i]
        if i == 4:
            right_chopstick = chopsticks[0]
        else:
            right_chopstick = chopsticks[i + 1]
        philosopher = Philosopher(philosopher_names[i], left_chopstick, right_chopstick)
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
