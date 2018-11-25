# cs533
Repo for cs533 final concurrency project
Create 5 applications (use python, java, C or whatever you want) and have them use each major type of unix communication to solve two classic concurrency/synchronization problems: producer-consumer and dining philosophers. Do this with pipes, shared memory, shared file,
TCP and MPI. Devise a way to test the correctness of each solution to each problem. Measure and compare performance and usability of each approach.

To download the mpi4py python package use the following command:
`pip install mpi4py`
or
`sudo apt-get install python-mpi4py`

(Note: on Mac you must first run `brew install mpich`, then `pip install mpi4py`)


To run MPI producer-consumer file:
`mpiexec -n 2 python3 mpi_pc.py`

To run MPI dining philosophers file:
`mpiexec -n 6 python mpi_diningphils.py`

