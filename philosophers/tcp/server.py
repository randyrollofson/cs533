# Server acts as the "waiter" in the dining philosophers problem.
# Server manages the distribution of the chopsticks to the philosophers

import socket
import pickle
import time
from threading import Thread, Lock


program_duration = 30
chopsticks = []

lock = Lock()

for i in range(5):
    chopstick = {
        "id": i,
        "in_use": False
    }
    chopsticks.append(chopstick)


class Server(Thread):
    running = True

    def run(self):
        host = "127.0.0.1"
        port = 12345

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))

        print("socket bound to port", port)
        s.listen(5)

        c, addr = s.accept()

        while self.running:
            r_data = c.recv(1024)
            try:
                recvd_data = pickle.loads(r_data)
            except EOFError:
                print("ending program")
                break
            action = recvd_data[0]
            philosopher = recvd_data[1]
            sticks = recvd_data[2]

            if action == "request":
                for j in range(len(sticks)):
                    print(philosopher, "requested chopstick", sticks[j])
                    send_data = self.request(sticks[j])
                    s_data = pickle.dumps(send_data)
                    print('Sending', philosopher, ': ', send_data)
                    c.send(s_data)
            elif action == "release":
                for j in range(len(sticks)):
                    print(philosopher, "releases chopstick", sticks[j])
                    self.release(sticks[j])
                send_data = "all done"
                s_data = pickle.dumps(send_data)
                print('Sending', philosopher, ': ', send_data)
                c.send(s_data)

        c.close()
        s.close()

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
print("Finishing...")
