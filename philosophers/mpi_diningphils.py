from mpi4py import MPI
import pickle
from threading import Thread, Lock
import time
from thread import *
import random

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
lock = Lock()

program_duration = 30
philosopher = None
chopsticks = []

# Client represents the 5 philosophers
if rank!=5:
    class Philosopher:

        def __init__(self, name, left_chopstick, right_chopstick):
            self.name = name
            self.chopstick1 = left_chopstick
            self.chopstick2 = right_chopstick

    class Client(Thread):
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
                    data = pickle.dumps(send_data)
                    try:
                        lock.acquire()
                        data = comm.bcast(data,root=rank)
                        #comm.send(send_data,dest=5,tag=11)
			lock.release()
                    except Exception as e:
			pass

                    try:
                        r_data = comm.bcast(data,root=rank)
                        #recv_data = comm.recv(source=MPI.ANY_SOURCE, tag=11)
                        recv_data = pickle.loads(r_data)
                    except Exception:
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
                data = pickle.dumps(send_data)
                try:
                    lock.acquire()
                    data = comm.bcast(data,root=rank)
                    lock.release()
                except:
                    pass

                try:
                    r_data = comm.bcast(data,root=rank)
                    recv_data = pickle.loads(r_data)
                except:
                    pass

                send_data = []
                if recv_data == -1:
                    print(self.philosopher_name, "failed to pick up chopstick 2, drops chopstick 1")
                    send_data.append("release")
                    sticks_to_release = []
                    send_data.append(self.philosopher_name)
                    sticks_to_release.append(chopstick1)
                    send_data.append(sticks_to_release)
                    data = pickle.dumps(send_data)
                    try:
                        lock.acquire()
                        data = comm.bcast(data,root=rank)
                        lock.release()
                    except:
                        pass

                    try:
                        r_data = comm.bcast(data,root=rank)
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
                    data = pickle.dumps(send_data)
                    try:
                        lock.acquire()
                        data = comm.bcast(data,root=rank)
                        lock.release()
                    except:
                        pass

                    try:
                        r_data = comm.bcast(data,root=rank)
                    except:
                        pass

                    time.sleep(random.random())

        def eat(self, philosopher):
            print(self.philosopher_name+" - starts eating")
            self.times_eating += 1
            time.sleep(random.random())
            print(self.philosopher_name+" - finishes eating, drops both chopsticks")

    client = Client()
    client.start()
    time.sleep(program_duration)
    client.running = False

    print("\nPhilosopher %d - Finishing..."%(rank+1))
    print("Philosopher %d - Waiting times: "%(rank+1), client.total_wait_time)
    print("Philosopher %d - Number of times eating: "%(rank+1),client.times_eating)
    time.sleep(2)

# Server acts as the "waiter" in the dining philosophers problem.
# Server manages the distribution of the chopsticks to the philosophers
elif rank == 5:
    class Server(Thread):
        running = True

        def run(self):
            while self.running:
		data = None
                r_data = comm.bcast(data,root=rank)
                
		try:
                    recvd_data = pickle.loads(r_data)
                except EOFError:
                    print("ending program")
                    break
		except Exception as e:
		    continue
                action = recvd_data[0]
                philosopher = recvd_data[1]
                sticks = recvd_data[2]

                if action == "request":
                    for j in range(len(sticks)):
                        print(philosopher+" - requested chopstick"+str(sticks[j]))
                        send_data = self.request(sticks[j])
                        s_data = pickle.dumps(send_data)
                        print('Sending '+philosopher+': '+str(send_data))
                        data = comm.bcast(s_data,root=5)
                elif action == "release":
                    for j in range(len(sticks)):
                        print(philosopher+" - releases chopstick"+str(sticks[j]))
                        self.release(sticks[j])
                    send_data = "all done"
                    s_data = pickle.dumps(send_data)
                    data = comm.bcast(s_data,root=5)

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


    server = Server()
    server.start()
    time.sleep(program_duration)
    server.running = False
    print("Waiter Finishing...")
