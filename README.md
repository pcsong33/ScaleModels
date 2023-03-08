## Scale Models and Logical Clocks

### File overview
* `main.py` - This is the main implementation of our scale model. which spawns three machines on separate processes with a random clock rate between 1 and 6. The machines connect to each other via client/server sockets to send messages to each other (following the rules of logical clocks and the assignment spec) for 1 minute. All events are written to CSV logs. To run: `python3 main.py`.
* `tests.py` - This is our unit test suite for the functions in `main.py`. It tests that log files are created and written to properly, that the server/client sockets are initialized correctly, that machines are able to send/receive messages from both the client and server connections, and that the machines are properly handling events and clock values. To run: `python3 test.py`.
* `logs/` - This directory contains the experimental data we used for analyzing and making observations about the scale model. All experiments were 1 minute long, with clock rates deterministically chosen.
* `notebook.md` - This is our lab notebook, which we used to track our ideas, progress, design decisions, etc. as we worked on the project.
* `analysis.ipynb` - TODO


### Design choices
* We implemented the scale mode using a de-centralized network. With centralized servers, there are scalability concerns, since there is a single point of failure: if the server goes down or experiences a failure, it can cause disruptions to all the clients. Our scale model distributes the message load and number of connections across all machines, reducing the reliance on the resources of a single machine. 
* Background thread for receiving messages: This allows messages to be received simultaneously for each machine, without disrupting the clock cycle that must process these incoming messages.
* Sockets: We used the sockets for machines to connect to each other in order for our implementation to be able to be deployed across multiple physical hosts.
* No shared data structures: All data structures are internal within each ModelMachine, so that there is no concurrency overhead as the model scales.