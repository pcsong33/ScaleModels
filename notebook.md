## 2/28/23
This initial entry is a synthesis of the materials from the 2/27 lecture and the Lamport reading that pertain to the Scale Models project. We also outline some initial first steps.
The Lamport paper presents two implementation rules for logical clocks. Let $T_e = C_i(e)$ be the value that the logical clock $C_i$ for process $P_i$ assigns to an event $e$:

1. **IR1:** Each process $P_i$ increments $C_i$ between any two events
2. **IR2:**
   1. If event a represents the sending of a message $m$, then $T_m = C_i(a)$
   2. Upon receiving message $m$, process $P_j$ sets $C_j$ greater than or equal to its present value and greater than $T_m$.

In accordance to the specifications described in lecture, we will represent values of events as non-negative integers. A process will increment their clock value by 1 after each event. If $e$ and $e'$ are consecutive events in a process $P_i$, and $e'$ is an event from a different process, $P_i$ will update $C_i$ in the following manner:
$$C_i(e') = \max(C_i(e), T_e') + 1$$
where $T_e$ is the receive event's timestamp.

Questions
1. Is there a need to keep a history of previous $C_i(e)$ values? Or is it sufficient to keep track of the current clock time in a single variable?
2. How should we think about handling the message queue? Professor Waldo mentioned that message queuing is something that socket libraries handle, so we may need to do more research into this.

Initial code contains just the logic for generating a random clock rate and sleeping for a tick of time. Most likely will need to split into server and client-side code for defining process behavior.

