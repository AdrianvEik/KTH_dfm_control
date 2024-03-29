
import dfmcontrol as dfmc
import dfmcontrol.Helper as dfmh

from dfmcontrol.Utility.pop import bitpop,uniform_bit_pop, normal_bit_pop, cauchy_bit_pop
from dfmcontrol.Helper import ndbit2int, int2ndbit
from dfmcontrol.Mathematical_functions import michealewicz
from dfmcontrol.Optimisation.DFM_opt_alg import genetic_algoritm

import numpy as np
import matplotlib.pyplot as plt

# Create a genetic algorithm object
ga = genetic_algoritm(bitsize=16)
ga.mode = "minimisation"
tfunc = michealewicz

# use the default bit2num function
ga.b2n = dfmh.ndbit2int

# The range of possible floats is now -10 to 10
ga.b2nkwargs = {"factor": 10}

# Initiate a population of 16 individuals with 2 genes each
ga.init_pop(uniform_bit_pop, shape=[2000, 2], bitsize=ga.bitsize, factor=ga.b2nkwargs["factor"],
            boundaries=[-10, 10])

# Initiate the log
ga.logdata(2)

# Set the target function
ga.target_func(tfunc)

# Set the selection, mutation and crossover functions
ga.set_select(dfmc.Utility.selection.rank_tournament_selection) # Rank selection
ga.set_mutate(dfmc.Utility.mutation.mutate) # Mutate the full bit (do not use for IEEE 754 floats)
ga.set_cross(dfmc.Utility.crossover.equal_prob) # Crossover the full bit (do not use for IEEE 754 floats)

ga.elitism = 4  # Keep the 4 best individuals
# Run the genetic algorithm

# The runcond argument is a string that is evaluated as a condition for the algorithm to stop
# The string can use any of the attributes of the genetic algorithm object
runcond = r"self.epoch < 10"  # Stop when the minimum distance from the best solution to the mathematical is less than 0.1

# The verbosity argument is an integer that controls the amount of output
# 0: No output
# 1: Output the current generation, (best & group) distance to the best solution and the best fitness
verbosity = 2

# The muargs argument is a dictionary that is passed to the mutation function as the kwargs argument
muargs = {"mutate_coeff": 4}

# The selargs argument is a dictionary that is passed to the selection function as the kwargs argument
selargs = {"nbit2num": ga.b2n, "fitness_func": dfmc.Utility.selection.no_fitness,
            "allow_duplicates": True}

ga.run(muargs=muargs, selargs=selargs, verbosity=verbosity, runcond=runcond)


ga.log.value.plot2d(tfunc, -10, 10, epoch=0)


