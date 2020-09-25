# PathFinding
This is from my CS170 class and this repo does not contain the input and output files, as they were used for grading purposes.
Due to the randomness of our algorithm, consequent outputs stemming from the same inputs will likely be different. Simulated Annealing calls for the search of the solution space as a way of avoiding local maxima's. This is achieved through the decision to make random choices.

The manager.py file helps create the output files by having multiple background workers. The workers run the Simulated Annealing algorithm for a fixed amount of time depending on the parameters defined in solver.py. We decided to use AWS EC2 instances to keep the workers running as the more time the simulated annealing algorithm is giving, the more desireable the solution becomes.

In order to generate all output files, you need to run manager.py and provide the proper input files. Note that when our group was running this procedure, we split up the input files among the different local computers we had available; running manager.py as is will likely take a very long time as it will run our algorithm on all the input files concurrently.
