import random

import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp
import sys

from typing import Union, Callable, List
from time import sleep, time

try:
    from .DFM_opt_alg import genetic_algoritm, full_mutate
    from .cross_funcs import equal_prob
    from dfmcontrol.Helper import ndbit2int
    from .selection_funcs import *
    from dfmcontrol.Log import log_object, log
    from dfmcontrol.Mathematical_functions import tfx_decorator

    from dfmcontrol.AdrianPackv402.Helper import compress_ind

except ImportError:
    from dfmcontrol.Optimisation import genetic_algoritm, mutate
    from dfmcontrol.Utility.crossover import equal_prob
    from dfmcontrol.Helper import ndbit2int
    from dfmcontrol.Utility.selection import *
    from dfmcontrol.Log import log_object, log
    from dfmcontrol.Mathematical_functions import tfx_decorator

    from dfmcontrol.AdrianPackv402.Helper import compress_ind


## global variables
individuals: int = 30
points_per_indv: int = 20
points_stability_test = 25

runtime = 10 # runtime in seconds
epoch = 0  # ??

# Hardcoded value for 39ch mirror
individual_size = 39

test_setup = True

# Logs intensity of stability test and algorithm
# array of dim 4, saved as dim 5 after run [epochs, 2: [stability, test], individuals, 3: [intensity, time, bin combination], sample size]
# sample size for algorithm -> points_per_indiv
# sample size of stability test -> points_stability_test (uses floating point average to compress to length sample size algorithm)
intens_blueprint = np.zeros(shape=[2, individuals, 3, points_per_indv])
intens: List[np.ndarray] = [intens_blueprint.copy()]
# Lookup table for voltages indexed in array "intens"
individual_table_blueprint = np.zeros(shape=[individuals, 2, individual_size])
individual_table: List[np.ndarray] = [np.zeros(shape=[individuals, 2, individual_size])]

"""How to find a voltage:
# Find the number of the individual in intens;
idx = intens[epoch, testtype, individual, 3, sample] ## sample # doesnt matter since for each sample the combination is the same
# Use this index to find the voltage combination in individuals;
indv = individuals[epoch][idx, testtype, :] ## this is the voltage combination
# Convert to binary using the ga.b2n() method;
ga.b2n(indv, **ga.b2nkwargs)
"""

# time intensity logs the intensity each time read_pm is called and logs the according time
# array of dim 1 saved as dim 2 after run [entries, 2: [intens, time]]
time_intens: List[np.ndarray] = [np.zeros(2)]

optimum: float = 100

t0 = time()

if __name__ == "__main__" and not test_setup:
    print("start")

    # Opening the mirror handle
    import okotech_lib.okodm_sdk.python.okodm_class as oko
    import sys

    handle = oko.open("MMDM 39ch,15mm",
                      "USB DAC 40ch, 12bit")  # handle for other functions

    if handle == 0:
        sys.exit(("Error opening OKODM device: ", oko.lasterror()))

    # Get the number of channels
    n = oko.chan_n(handle) # Should be 39

    print("n channels= ", n)

    ## Opening the DMMM
    import pyvisa
    from ThorlabsPM100 import ThorlabsPM100

    rm = pyvisa.ResourceManager()

    print(rm.list_resources())
    inst = rm.open_resource('USB0::0x1313::0x8078::P0000874::INSTR', timeout=1)

    power_meter = ThorlabsPM100(inst=inst)

    def read_pm():
        global time_intens
        time_intens.append(np.array([power_meter.read, time() - t0]))
        return time_intens[-1][0]

    def set_voltage(voltages):
        try:
            if not oko.set(handle, voltages):
                sys.exit("Error writing to OKODM device: " + oko.lasterror())
        except:
            voltages = np.zeros(shape=n)
            if not oko.set(handle, voltages):
                sys.exit("Error writing to OKODM device: " + oko.lasterror())

elif test_setup:
    n = 39

    def read_pm():
        global time_intens
        time_intens.append(np.array([np.exp(random.random()), time() - t0]))
        return time_intens[-1][0]

    def set_voltage(voltages):
        pass




## Additional functions for the algorithm

def tfmirror(*args, **kwargs):
    """
    Takes an individual and sets the mirror to the corresponding voltage

    :param individual: Individual to be set
    :param handle: Handle for the mirror
    :param n: Number of channels
    :return: None
    """
    global intens, optimum, epoch, points_per_indv

    if "pop" in kwargs:
        pop = kwargs["pop"]
    else:
        pop: np.ndarray = args[0]

    b2n: Callable = kwargs["b2n"]
    b2nkwargs: dict = kwargs["b2nkwargs"]

    ppi: int = kwargs.get("points_per_indv", 100)
    stability: bool = kwargs.get("stability", False)

    num_pop = b2n(pop, bitsize, **b2nkwargs)

    # Values are normalised, how much time does this take?
    for indiv in num_pop:
        for var in indiv:
            try:
                assert -1 < var < 1
            except AssertionError:
                voltages = np.zeros(shape=n)
                set_voltage(voltages)

                raise ValueError("Input voltage can not be > 1 or < -1")

    avg_read = np.zeros(num_pop.shape[0])

    i = 0
    print(num_pop.shape)
    for indiv in num_pop:
        voltages = indiv

        set_voltage(voltages)

        # Read the power meter
        compress_this = np.zeros([2, ppi])
        for j in range(ppi):
            if stability:
                compress_this[0, j] = read_pm()
                compress_this[1, j] = time() - t0
            else:
                intens[epoch][1, i, 0, j] = read_pm()
                intens[epoch][1, i, 1, j] = time() - t0
                intens[epoch][1, i, 2, j] = i
                individual_table[epoch][i, 1, :] = indiv

        if stability:
            this_compressed_intens = compress_ind(compress_this[0, :], points_per_indv)[0]
            this_compressed_time = compress_ind(compress_this[1, :], points_per_indv)[0]
            intens[epoch][0, i, 0, :] = this_compressed_intens
            intens[epoch][0, i, 1, :] = this_compressed_time
            intens[epoch][0, i, 2, :] = np.full(points_per_indv, i, dtype=int)
            individual_table[epoch][i, 0,:] = indiv

        if stability:
            avg_read[0] = np.average(intens[epoch][0, i, 0, :])
        else:
            avg_read[i] = np.average(intens[epoch][1, i, 0, :])/optimum

        i += 1
        # Test out on DFM and append intensity
        # Divide intensity by global var optimum

    set_voltage(np.zeros(shape=n))

    return avg_read


def select(*args, **kwargs):
    """
    Selects the best individuals from the population based on rank selection
    :param args:  population, fitness, k
    :param kwargs:  None
    :return:  selected individuals
    """
    global intens, optimum, points_per_indv, epoch, points_stability_test

    pop = args[0]

    kwargs["points_per_indv"] = points_per_indv
    kwargs["stability"] = False

    fitness = tfmirror(*args, **kwargs)

    # probability paramter for rank selection
    prob_param = 1.9
    if "p" in kwargs:
        prob_param = kwargs["p"]

    fit_rng = np.flip(np.argsort(fitness))

    # Test the best individual for stability
    kwargs["points_per_indv"] = points_stability_test
    kwargs["stability"] = True
    kwargs["pop"] = pop[fit_rng[0]]

    tfmirror(**kwargs)

    p = (prob_param * (1 - prob_param)**(np.arange(1, fitness.size + 1, dtype=float) - 1))
    p = p/np.sum(p)

    selection_array = np.zeros(fit_rng.shape)
    for i in range(fitness.size):
        selection_array[fit_rng[i]] = p[i]

    pind = []
    rng = np.arange(0, fitness.size)

    for i in range(int(fitness.size / 2)):
        if selection_array.size > 1:
            try:
                par = np.random.choice(rng, 2, p=selection_array,
                                       replace=False)
            except ValueError:
                if kwargs["verbosity"] == 1:
                    print("Value error in selection, equal probability")

                selection_array = np.full(selection_array.size,
                                          1 / selection_array.size)
                par = np.random.choice(rng, 2, p=selection_array,
                                       replace=False)

            pind.append(list(sorted(par).__reversed__()))

    set_voltage(np.zeros(shape=n))

    return pind, fitness, p, fitness


class log_intensity(log_object):
    """
    Class for logging the intensity

    """
    def __init__(self, b2num, bitsize, b2nkwargs, *args, **kwargs):
        super().__init__(b2num, bitsize, b2nkwargs, *args, **kwargs)
        self.intensity = []
        self.intens_time = []
        self.indivuals = []

    def update(self, data, *args):
        global intens
        self.data.append(data)
        self.epoch.append(len(self.data))
        print("saves:", np.asarray(intens.copy()).shape)

        self.intensity = intens.copy()
        self.intens_time = time_intens.copy()
        self.indivuals = individual_table.copy()


    def __copy__(self):
        log_intens_c = log_intensity(self.b2n, self.bitsize, self.b2nkwargs)
        log_intens_c.intensity = self.intensity
        log_intens_c.data = self.data
        log_intens_c.indivuals = self.indivuals
        log_intens_c.intens_time = self.intens_time
        log_intens_c.epoch = self.epoch

        return log_intens_c

    def save2txt(self, data: Union[str, list], filename: str, sep: str = ";"):
        """
        Saves data from the intens matrix or from an log_intensity attr to a txt file

        :param data:  str or list of str, data to be saved
        :note: binary data does not function properly

        :param filename:  str, filename
        :param sep:  str, seperator

        :return:  None
        """

        # get the data
        try:
            # If the data is in the intens matrix create a submatrix with the
            # data
            idxs = ["intensity", "time", "binary"]
            if data in idxs or isinstance(data, list):
                if isinstance(data, str):
                    if data in ["time", "intensity"]:
                        submat = np.asarray(self.intensity)[:, 1, :, idxs.index(data)]
                        submat = np.apply_over_axes(np.average, submat, 2).reshape([submat.shape[0], submat.shape[1]]).T
                    elif data == "binary":
                        cmat = np.asarray(self.intensity)[:, 1, :,
                               idxs.index(data), 0].astype(int)
                        indmat = np.asarray(self.indivuals)[:, 1, :]
                        cmat = indmat[:, 0, cmat]
                        submat = cmat.T

                # If more than one data type is selected, concatenate them
                elif isinstance(idxs, list):
                    # Intensity and time should go before binary in the data param
                    # otherwise the binary data will be averaged, so raise error
                    if idxs[0] == "binary":
                        raise ValueError("Binary data should be last in data param")

                    # Create a submatrix for each data type and concatenate them
                    # Start with intensity and time
                    submat = np.asarray(self.intensity)[:, 1, :, idxs.index(data[0])]
                    submat = np.apply_over_axes(np.average, submat, 2).reshape([submat.shape[0], submat.shape[1]]).T

                    for i in range(1, len(data)):
                        # If the requested data is time or intensity, average over the points per individual to get a
                        # single value.
                        if data[i] in ["time", "intensity"]:
                            cmat = np.asarray(self.intensity)[:, 1, :, idxs.index(data[i])]
                            cmat = np.apply_over_axes(np.average, cmat, 2).reshape([cmat.shape[0], cmat.shape[1]]).T
                            submat = np.concatenate([submat, cmat], axis=1)
                        # If the requested data is binary, use the indexes in intensity to get the binary values from individual_table
                        else:
                            cmat = np.asarray(self.indivuals)[:, 1, :, idxs.index(data[i])]
                            cmat = individual_table[cmat]
                            print(cmat)


                data = submat
            else:
                data = np.array(getattr(self, data)).T

        except AttributeError:
            raise AttributeError(
                "The data '%s' does not exist in the log object '%s'." % (
                data, self.__class__.__name__))

        # Save to text file with separator sep
        with open(filename, "w") as f:
            f.write(sep.join(str(i) for i in range(len(self.intensity))) + "\n")
            for i in range(len(data)):
                f.write(
                    sep.join(str(data[i, j]) for j in range(data.shape[1])) + "\n")

    def plot(self, epoch: Union[slice, int] = slice(0, None),
             individual: Union[slice, int] = slice(0, None),
             data: Union[slice, int] = 0,
             fmt_data: str = "average", linefmt="scatter") -> None:
        """
        Plots the intensity of the individuals

        :param epoch: Slice of epochs to plot
        :param individual: Slice of individuals to plot
        :param data: Slice of data to plot
        :param fmt_data: Format of the data to plot 'average' or 'raw'
        :param linefmt: Format of the line to plot 'scatter' or 'line'

        :return: None
        """

        if fmt_data.lower() == "raw":
            int_mat = np.asarray(self.intensity)[epoch, 1, individual, data, :]
        else:
            int_mat = np.apply_over_axes(np.average,
                                         np.asarray(self.intensity)[epoch, 1, individual, data, :],
                                         2)

        for line in range(int_mat.shape[1]):
            # take the amount of epochs
            x = np.array([np.full(int_mat.shape[2], i) for i in range(int_mat.shape[0])]).flatten()

            # plot their intensity at each epoch
            # x = [0, 1, ... epoch n]
            # y = [intens of indv 'line' @ epoch 0, @ epoch 1, @ epoch 2, ... @ epoch n]
            y = int_mat[:, line].flatten()

            if linefmt == "scatter":
                plt.scatter(x, y, label="individual %s" % line)
            else:
                plt.plot(x, y, label="individual %s" % line)

        plt.xlabel("epoch")
        plt.ylabel("Intensity")

        plt.legend()
        plt.show()
        return None

    def animate(self):

        return None

class mirror_alg(genetic_algoritm):
    """
    Class for the genetic algorithm implentation of the mirror algorithm
    """
    def __init__(self, dtype: str = "float", bitsize: int = 32,
                 endianness: str = "big"):
        super().__init__(dtype, bitsize, endianness)
        self.tfunc = tfx_decorator(tfmirror, 39)

        # self.log.__add__(log_intensity(self.b2n, self.bitsize, self.b2nkwargs))

    def run(self, selargs: dict = {},
            cargs: dict = {}, muargs: dict = {},
            target: float = 1, verbosity: int = 1):
        """
        Runs the genetic algorithm.

        :param cargs: Arguments for the crossover function
        :param muargs: Arguments for the mutation function
        :param seedargs: Arguments for the seed function
        :param selargs: Arguments for the selection function
        :param epochs: Number of epochs to run
        :param verbosity: Verbosity of the algorithm

        :return: None
        """
        global epoch, optimum, points_per_indv, points_stability_test

        if len(self.pop) == 0:
            self.init_pop()

        self.target = target

        selargs["fx"] = self.tfunc
        selargs["bitsize"] = self.bitsize
        selargs["b2n"] = self.b2n
        selargs["b2nkwargs"] = self.b2nkwargs
        selargs["verbosity"] = verbosity
        selargs["avoid_calc_fx"] = True
        selargs["points_per_indv"] = points_per_indv
        selargs["points_stability_test"] = points_stability_test

        parents, fitness, p, fx = self.select(self.pop, **selargs)

        # if self.seed.__name__ == "none":
        #     self.epochs = int(np.floor(np.log2(self.shape[0])))

        if self.dolog:
            # Highest log level
            rank = []
            for ppair in parents:
                rank.append(self.pop[ppair[0]])
                rank.append(self.pop[ppair[1]])
            rank = np.asarray(rank)

            if self.dolog == 2:
                self.log.ranking.update(rank, fx, np.full(39, 0), 0)
                self.log.time.update(time() - self.tstart, self.tfunc.calculations)
                self.log.selection.update(parents, p, fitness)
                self.log.log_intensity.update(self.pop)

                if len(self.log.add_logs) > 1:
                    for l in self.log.add_logs[0:]:
                        l.update(data=self.pop)

                self.log.sync_logs()

            elif self.dolog == 1:
                self.log.ranking.update(rank, fx, np.full(39, 0), 0)
                self.log.time.update(time() - self.tstart)

        while True:
            if np.average(intens[epoch][0, 0, 0, :]) < self.target:
                newgen = []
                if verbosity:
                    print("%s/%s" % (epoch + 1, self.epochs))

                selargs["points_per_indv"] = points_per_indv
                selargs["pop"] = self.pop
                selargs["stability"] = False

                cargs["bitsize"] = self.bitsize
                muargs["bitsize"] = self.bitsize

                for ppair in parents[self.elitism:]:
                    child1, child2 = self.cross(self.pop[ppair[0]], self.pop[ppair[1]], **cargs)

                    newgen.append(child1)
                    newgen.append(child2)


                for ppair in parents[:self.elitism]:
                    child1, child2 = self.cross(self.pop[ppair[0]], self.pop[ppair[1]], **cargs)
                    newgen.append(self.mutation(child1, **muargs))
                    newgen.append(self.mutation(child2, **muargs))



                # Select top10
                t10 = parents[:self.save_top]

                self.genlist.append([])
                # print(self.genlist[epoch+1])
                for ppair in t10:
                    self.genlist[epoch].append(self.pop[ppair[0]])
                    self.genlist[epoch].append(self.pop[ppair[1]])

                self.genlist[epoch] = np.array(self.genlist[epoch])

                # genlist.append(rpop)
                self.pop = np.array(newgen)
                parents, fitness, p, fx = self.select(np.array(newgen), **selargs)

                if self.dolog:
                    # Highest log level
                    rank = np.zeros(self.pop.shape)
                    if self.dolog == 2:
                        rankind = np.argsort(fitness)

                        j = 0
                        for i in rankind:
                            rank[j] = self.pop[i]
                            j += 1

                        self.log.ranking.update(rank, fx, np.full(39, 0), self.target)
                        self.log.time.update(time() - self.tstart, self.tfunc.calculations)
                        self.log.selection.update(parents, p, fitness)
                        self.log.value.update(self.pop, self.genlist[epoch])
                        self.log.log_intensity.update(self.pop, intens.copy(),
                                                      time_intens.copy(),
                                                      individual_table.copy())

                        # self.log.log_intensity.update(self.pop, intens.copy())

                        # if additional logs added by appending them after initiation of self.log
                        # go through them and update with the population
                        # other data can be found within other logs and data
                        # can be added by using global statements or other.
                        if len(self.log.add_logs) > 1:
                            for l in self.log.add_logs:
                                l.update(data=self.pop)

                        self.log.sync_logs()


                    elif self.dolog == 1:
                        self.log.ranking.update(rank, fx, self.tfunc.minima["x"], self.tfunc.minima["fx"])
                        self.log.time.update(time() - self.tstart)

                selargs["points_per_indv"] = points_stability_test
                selargs["stability"] = True
                selargs["pop"] = self.pop[np.where(np.max(fitness) == fitness)[0][0]]

                tfmirror(**selargs)

                print(np.average(intens[epoch][0, 0, 0, :]))

                epoch += 1
                self.results = self.genlist

                print(np.asarray(intens).shape)

                intens.append(intens_blueprint)
                individual_table.append(individual_table_blueprint)

            else:
                break
                set_voltage(individual_table[int(intens[epoch][0, 0, 2, 0])])



class Process(mp.Process):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)




## Algorithm

from time import time

k = 4
bitsize = 8
n = 39
size = [individuals, n]

ga = mirror_alg(bitsize=bitsize)


def t():
    return time() - t0


def main():
    global time_intens

    ga.optimumfx = optimum
    print(size)

    ga.b2n = ndbit2int


    ga.init_pop("cauchy", shape=[size[0], size[1]], bitsize=bitsize, loc=0, scale=1)
    print(ga.pop.shape)
    print(ga.log.creation)
    ga.b2nkwargs = {"factor": 1, "normalised": True, "bias": 0.0}

    ga.elitism = 4


    ga.logdata(2)
    ga.log.append(log_intensity(ga.b2n, ga.bitsize, ga.b2nkwargs))

    # ga.seed = uniform_bit_pop_IEEE
    ga.set_cross(equal_prob)
    ga.set_mutate(mutate)
    ga.set_select(rank_tournament_selection)

    # P value for population of 20?
    p = 0.01
    ga.log.ranking.epoch.append(0)

    print("start run")
    ga.run(muargs={"mutate_coeff": 3},
           selargs={"nbit2num": ndbit2int,
                    "b2n": ga.b2n,
                    "b2nkwargs": ga.b2nkwargs,
                    "p": p,
                    "fitness_func": no_fitness
                    },
           verbosity=1,
           target=1.6)

    # print(ga.log.log_intensity.intensity)
    ga.log.log_intensity.save2txt(["time", "intensity"], "intensity.txt")

    k = 4
    path = "test%s" % k
    ga.save_log(path + ".pickle")
    np.savetxt(path + ".txt", np.asarray(time_intens))

    # ga.log.log_intensity.plot(fmt_data = "raw", individual = slice(0, 1))
    # ga.save_log("dfmtest_data%s.pickle" % k)


def checkruntime():
    sleep(runtime)
    return True

# for i in np.linspace(0.01, 0.1, 10):
try:
    if __name__ == "__main__":
        print("time: ", time() - t0)

        main()
        # with mp.Pool(2) as p:
        #     worker1 = p.apply_async(main, [])
        #     worker2 = p.apply_async(checkruntime, [])
        #
        #     worker2.wait()
        #     p.close()

    # main()
    # except:
    #     voltages = np.zeros(shape=n)
    #
    #     if not oko.set(handle, voltages):
    #         sys.exit("Error writing to OKODM device: " + oko.lasterror())
    #
    #     print("Voltages set to zero")

except Exception as e:
    print('\x1b[33m' + "Exception: %s " % e + '\x1b[0m')

finally:
    if __name__ == "__main__":
        k = 6
        k += 1

        # print(intens)

        set_voltage(np.zeros(shape=n))

        print("Mirror voltages set to zero")
        # print("Final best intensity: %s" % bestintens[-1, 0])
        print("Execution time: %s" % (time() - t0))
        print(r"Log saved to src\dfmtest_data%s.pickle" % k)
        print("Done")


main()


