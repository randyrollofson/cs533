import os, time, threading,sys
from threading import Thread, Condition
import random
import errno

pipe1 = "/tmp/myPipe_1"				# Pipe location
if not os.path.exists(pipe1):		# Create Named Pipe if not exist
    os.mkfifo(pipe1)

condition = Condition()


class ProducerThread(Thread):
	running = True
	total_wait_time = 0
	total_digits_produced = 0

	def run(self):
		nums = range(5)
		fifo_out = os.open(pipe1, os.O_NONBLOCK|os.O_RDWR)  # Open pipe in nonBlocking mode
		while self.running:
			condition.acquire()
			num = random.choice(nums)
			line = os.write(fifo_out,(str(num)).encode())   # Write in pipe
			self.total_digits_produced += 1
			print("Producer Writing...")
			print("Producer writes: %d\n" % num)
			condition.notify()
			condition.release()
			time.sleep(random.random())

class ConsumerThread(Thread):
	running = True
	total_wait_time = 0
	total_digits_consumed = 0
	def run(self):
		fifo_in = os.open(pipe1, os.O_RDONLY|os.O_NONBLOCK) #Open Pipe in nonBlocking mode
		while self.running:
			condition.acquire()

			try:
				buffer = os.read(fifo_in,1)			# read from pipe
			except OSError as err:
				if err.errno == errno.EAGAIN or err.errno == errno.EWOULDBLOCK:
					buffer = None		# Empty Pipe
				else:
					raise

			if buffer is None: 			# If Pipe is empty then wait for producer to write
				print("Nothing in file to read, consumer is waiting...")
				t0 = time.time()
				condition.wait()
				t1 = time.time()
				self.total_wait_time += (t1 - t0)
				print("Producer added something to queue and notified the consumer!\n")	
			else:
				print("Consumer Readings...")		
				print("Consumer Reads: %s\n" % buffer.decode())
				self.total_digits_consumed += 1
	
			condition.notify()
			condition.release()
			time.sleep(random.random())

p = ProducerThread()
c = ConsumerThread()

p.start()
c.start()

time.sleep(10)	

p.running = False
c.running = False

print("total producer wait time: ", p.total_wait_time)
print("total consumer wait time: ", c.total_wait_time)
print("Total digits produced:", p.total_digits_produced)
print("Total digits consumed:", c.total_digits_consumed)