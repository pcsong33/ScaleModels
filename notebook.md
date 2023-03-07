## 3/6/23
We've begun creating some unit tests. Code in `main.py` was slightly refactored to enable
cleaner testing. 

Current Unit Test Coverage:
1. `init_logs`
2. `update_logs`

We've also handled the exiting gracefully task by sending a "shutdown" message when the time limit has finished.

Finally, we've run some experiments (data in `logs/`) with deterministic clock rates in order to see the impact of different clock rates on the logs. Experiments with prefix `0.25internal` have a lowered 1/4 chance of an event being internal (i.e. we generate a random number from 1 to 4 instead of 1 to 10). Some preliminary observations:
* When rates are constant across all machines, then there seem to be no gaps and logical_clock // clock_rate = global_clock as expected.
* When rates differ across machines, no gaps seem to occur for the machine with the largest rate. Gaps do however occur for the other machines. Queue lengths get long for the machine with lowest clock rate, and they spend much more time receiving messages than sending/internal operations.
* A guess: likely there is less drift if the differences are less stark, e.g. 4,4,4 vs 3,4,5 vs 1,3,6
* The reason for drift is that all of the logical clocks are incrementing by 1 even though the machines have different speeds. So to fix this, I tried changing the increment value for each event from 1 to `1 / self.clock_rate` instead, and ran experiments with rates 1,3,6 with this modification (the logs with prefix `propinc`). Sure enough, there appears to be no drift, though I predict that the proportion of send/receive/internal is about the same. This is quite interesting; I wonder why logical clocks aren't defined as such in the first place. Likely because in practice, you wouldn't actually know the precise relative/absolute relationships of machine speeds?

## 3/5/23
We've coded an implementation of the scale model using processes and threads. A design and scalability explanation is described below.
### Design
Upon program initialization, three processes are started. The processes are given 
2 ports: one port to connect server-side and one port to connect client-side. Messages
are received via background threads listening on both the server and client ports. Every clock cycle,
an event (receive message, send message, internal event) is logged in a csv file for each process.

### Scalability
With this model, we can scale to $n$ processes, by creating ${n\choose 2}$ total connections between all of the processes. Since the sockets 
are bidirectional, only one of the processes need to initialize a connection request.

Things to do:
1. Write tests. According to the 2/27 lecture, unit tests do not need to be end-to-end, 
but need to test smallest units of functioning code. 
2. Run experiments. It would be comprehensive to perhaps run multiple trials with deterministic clock rates, to better analyze the data and understand average performance. 
3. Exit Gracefully. Not high priority, but find a way to close sockets and threads and shutdown machines gracefully.


## 2/28/23
This initial entry is a synthesis of the materials from the 2/27 lecture and the Lamport reading that pertain to the Scale Models project. We also outline some initial first steps.
The Lamport paper presents two implementation rules for logical clocks. Let $T_e = C_i(e)$ be the value that the logical clock $C_i$ for process $P_i$ assigns to an event $e$:

1. **IR1:** Each process $P_i$ increments $C_i$ between any two events
2. **IR2:**
   1. If event a represents the sending of a message $m$, then $T_m = C_i(a)$
   2. Upon receiving message $m$, process $P_j$ sets $C_j$ greater than or equal to its present value and greater than $T_m$.

In accordance to the specifications described in lecture, we will represent values of events as non-negative integers. A process will increment their clock value by 1 after each event. If $e$ and $e'$ are consecutive events in a process $P_i$, and $e'$ is an event from a different process, $P_i$ will update $C_i$ in the following manner:
$$C_i(e') = \max(C_i(e), T_{e'}) + 1$$
where $T_{e'}$ is the receive event's timestamp.

Questions
1. Is there a need to keep a history of previous $C_i(e)$ values? Or is it sufficient to keep track of the current clock time in a single variable?
2. How should we think about handling the message queue? Professor Waldo mentioned that message queuing is something that socket libraries handle, so we may need to do more research into this.

Initial code contains just the logic for generating a random clock rate and sleeping for a tick of time. Most likely will need to split into server and client-side code for defining process behavior.

