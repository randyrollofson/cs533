from mpi4py import MPI
from threading import Thread, Lock
import time
from _thread import *
import random

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
lock = Lock()

program_duration = 30
philosopher = None
chopsticks = []

#Philosopher_thread represents the 5 philosophers
if rank!=5:
    class Philosopher:

        def __init__(self, name, left_chopstick, right_chopstick):
            self.name = name
            self.chopstick1 = left_chopstick
            self.chopstick2 = right_chopstick

    class Philosopher_thread(Thread):
        running = True
        total_wait_time = 0
        times_eating = 0
        philosopher_name = None

        def run(self):
            self.philosopher_name = "Philosopher"+str(rank+1)
            left_chopstick = rank
            if rank == 4:
                right_chopstick = 0
            else:
                right_chopstick = rank+1
            philosopher = Philosopher(self.philosopher_name, left_chopstick, right_chopstick)
            start_new_thread(self.attempt_to_eat, (philosopher,))

        def attempt_to_eat(self, philosopher):
            chopstick1 = philosopher.chopstick1
            chopstick2 = philosopher.chopstick2

            while self.running:
                recv_data = -1
                t0 = time.time()
                print(self.philosopher_name+" - is waiting...")
                while recv_data == -1:
                    send_data = []
                    sticks_to_request = []
                    send_data.append("request")
                    send_data.append(self.philosopher_name)
                    sticks_to_request.append(chopstick1)
                    send_data.append(sticks_to_request)
                    try:
                        lock.acquire()
                        comm.send(send_data,dest=5,tag=11)
                        lock.release()
                    except Exception as e:
                        pass

                    try:
                        recv_data = comm.recv(source=5, tag=11)
                    except Exception as e:
                        print(e)
                        pass                      

                t1 = time.time()
                self.total_wait_time += (t1 - t0)

                print(self.philosopher_name+" - picks up chopstick 1, attempts to pick up chopstick 2")
                send_data = []
                sticks_to_request = []
                send_data.append("request")
                send_data.append(self.philosopher_name)
                sticks_to_request.append(chopstick2)
                send_data.append(sticks_to_request)
                try:
                    lock.acquire()
                    comm.send(send_data,dest=5,tag=11)
                    lock.release()
                except:
                    pass

                try:
                    recv_data = comm.recv(source=5, tag=11)
                except Exception as e:
                    print(e)
                    pass

                send_data = []
                if recv_data == -1:
                    print(self.philosopher_name, "failed to pick up chopstick 2, drops chopstick 1")
                    send_data.append("release")
                    sticks_to_release = []
                    send_data.append(self.philosopher_name)
                    sticks_to_release.append(chopstick1)
                    send_data.append(sticks_to_release)
                    try:
                        lock.acquire()
                        comm.send(send_data,dest=5,tag=11)
                        lock.release()
                    except:
                        pass

                    try:
                    	r_data = comm.recv(source=5, tag=11)
                    except:
                        pass

                    time.sleep(random.random())
                else:
                    sticks_to_release = []
                    print(self.philosopher_name+" - has both chopsticks!")
                    self.eat(philosopher)
                    send_data.append("release")
                    send_data.append(self.philosopher_name)
                    sticks_to_release.append(chopstick1)
                    sticks_to_release.append(chopstick2)
                    send_data.append(sticks_to_release)
                    try:
                        lock.acquire()
                        comm.send(send_data,dest=5,tag=11)
                        lock.release()
                    except:
                        pass

                    try:
                    	r_data = comm.recv(source=5, tag=11)
                    except:
                        pass

                    time.sleep(random.random())

        def eat(self, philosopher):
            print(self.philosopher_name+" - starts eating")
            self.times_eating += 1
            time.sleep(random.random())
            print(self.philosopher_name+" - finishes eating, drops both chopsticks")
    
    philosopher_thread = Philosopher_thread()
    philosopher_thread.start()
    time.sleep(program_duration)
    philosopher_thread.running = False

    time.sleep(rank+1)
    comm.send([(rank+1),philosopher_thread.total_wait_time,philosopher_thread.times_eating],dest=5,tag=11)
    print("\nPhilosopher %d - Finishing..."%(rank+1))
    print("Philosopher %d - Waiting times: "%(rank+1), philosopher_thread.total_wait_time)
    print("Philosopher %d - Number of times eating: "%(rank+1),philosopher_thread.times_eating)
    time.sleep(2)

#  This acts as the "waiter" in the dining philosophers problem.
# Waiter manages the distribution of the chopsticks to the philosophers
elif rank == 5:

    for i in range(5):
        chopstick = {
            "id": i,
            "in_use": False
        }
        chopsticks.append(chopstick)

    class Waiter (Thread):
        running = True

        def run(self):
            while self.running:
                data = None
                action = None
                recvd_data = comm.recv(source=MPI.ANY_SOURCE, tag=11)
                action = recvd_data[0]
                philosopher = recvd_data[1]
                sticks = recvd_data[2]
                destrank = int(philosopher[-1]) - 1
                if action == "request":
                    for j in range(len(sticks)):
                        print(philosopher+" - requested chopstick"+str(sticks[j]))
                        send_data = self.request(sticks[j])
                        comm.send(send_data,dest=destrank,tag=11)
                elif action == "release":
                    for j in range(len(sticks)):
                        print(philosopher+" - releases chopstick"+str(sticks[j]))
                        self.release(sticks[j])
                    send_data = "all done"
                    comm.send(send_data,dest=destrank,tag=11)

        def request(self, chopstick_id):
            for chopstick in chopsticks:
                if chopstick["id"] == chopstick_id and chopstick["in_use"] is False:
                    chopstick["in_use"] = True
                    return chopstick["id"]

            return -1

        def release(self, chopstick_id):
            for chopstick in chopsticks:
                if chopstick["id"] == chopstick_id:
                    chopstick["in_use"] = False

    waiter = Waiter()
    waiter.start()
    time.sleep(program_duration)
    waiter.running = False
    print("Finishing...")

    time.sleep(6)
    numPhils=5
    combined_throughput=0
    combined_wait_time=0
    tpt_time_data=[]
    while(numPhils!=0):
        recvd_data = comm.recv(source=MPI.ANY_SOURCE, tag=11)
        if recvd_data[0] in range(1,6):
            numPhils = numPhils-1
            combined_throughput = combined_throughput + recvd_data[2]
            combined_wait_time = combined_wait_time + recvd_data[1]

    print("Total Wait Time: %f"%combined_wait_time)
    print("Total Throughput: %d"%combined_throughput)

    time.sleep(2)
