# Client represents the 5 philosophers

import socket
import pickle
from threading import Thread
import time
from _thread import *
import random


program_duration = 10
philosophers = []


class Philosopher:
    total_wait_time = 0
    times_eating = 0

    def __init__(self, name, left_chopstick, right_chopstick):
        self.name = name
        self.chopstick1 = left_chopstick
        self.chopstick2 = right_chopstick


class Client(Thread):
    running = True

    def run(self):
        host = '127.0.0.1'
        port = 12345

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        for i in range(5):
            start_new_thread(self.attempt_to_eat, (s, philosophers[i]))

    def attempt_to_eat(self, s, philosopher):
        chopstick1 = philosopher.chopstick1
        chopstick2 = philosopher.chopstick2

        while self.running:
            recv_data = -1
            t0 = time.time()
            print(philosopher.name, "is waiting...")
            while recv_data == -1:
                send_data = []
                sticks_to_request = []
                send_data.append("request")
                send_data.append(philosopher.name)
                sticks_to_request.append(chopstick1)
                send_data.append(sticks_to_request)
                data = pickle.dumps(send_data)
                try:
                    s.send(data)
                except:
                    pass

                try:
                    r_data = s.recv(1024)
                    recv_data = pickle.loads(r_data)
                except:
                    pass

            t1 = time.time()
            philosopher.total_wait_time += (t1 - t0)

            print(philosopher.name, "picks up chopstick 1, attempts to pick up chopstick 2")
            send_data = []
            sticks_to_request = []
            send_data.append("request")
            send_data.append(philosopher.name)
            sticks_to_request.append(chopstick2)
            send_data.append(sticks_to_request)
            data = pickle.dumps(send_data)
            try:
                s.send(data)
            except:
                pass

            try:
                r_data = s.recv(1024)
                recv_data = pickle.loads(r_data)
            except:
                pass

            send_data = []
            if recv_data == -1:
                print(philosopher.name, "failed to pick up chopstick 2, drops chopstick 1")
                send_data.append("release")
                sticks_to_release = []
                send_data.append(philosopher.name)
                sticks_to_release.append(chopstick1)
                send_data.append(sticks_to_release)
                data = pickle.dumps(send_data)
                try:
                    s.send(data)
                except:
                    pass

                print(philosopher.name, "swaps chopstick order for next time")
                temp = chopstick2
                chopstick2 = chopstick1
                chopstick1 = temp
            else:
                sticks_to_release = []
                print(philosopher.name, "has both chopsticks!")
                self.eat(philosopher)
                send_data.append("release")
                send_data.append(philosopher.name)
                sticks_to_release.append(chopstick1)
                sticks_to_release.append(chopstick2)
                send_data.append(sticks_to_release)
                data = pickle.dumps(send_data)
                try:
                    s.send(data)
                except:
                    pass

            try:
                s.recv(1024)
            except:
                pass
            time.sleep(random.random())
        s.close()

    def eat(self, philosopher):
        print(philosopher.name, "starts eating")
        philosopher.times_eating += 1
        time.sleep(random.random())
        print(philosopher.name, "finishes eating, drops both chopsticks")


def create_philosophers():
    chopsticks = []
    for i in range(5):
        chopsticks.append(i)

    philosopher_names = ['Philosopher 1', 'Philosopher 2', 'Philosopher 3', 'Philosopher 4', 'Philosopher 5']

    for i in range(5):
        left_chopstick = chopsticks[i]
        if i == 4:
            right_chopstick = chopsticks[0]
        else:
            right_chopstick = chopsticks[i + 1]
        philosopher = Philosopher(philosopher_names[i], left_chopstick, right_chopstick)
        philosophers.append(philosopher)


create_philosophers()
client = Client()
client.start()
time.sleep(program_duration)
client.running = False

print("Finishing...")
print("\nWaiting times:")
for philosopher in philosophers:
    print(philosopher.name, ": ", philosopher.total_wait_time)

print("\nNumber of times eating:")
for philosopher in philosophers:
    print(philosopher.name, ": ", philosopher.times_eating)

