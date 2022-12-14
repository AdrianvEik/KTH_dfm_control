from typing import Callable
from datetime import datetime

from mpl_toolkits.axes_grid1 import make_axes_locatable

from helper import convertpop2n
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from AdrianPackv402.Aplot import Default

def pythagoras(x):
    return np.sqrt(sum(x))


class log:

    def __init__(self, pop, select, cross, mutate, b2n, elitism, savetop,
                 bitsize: int, b2nkwargs: dict):
        # Pop
        self.pop = pop
        self.bitsize = bitsize

        # Logs
        self.time = log_time(b2n, bitsize, b2nkwargs)
        self.ranking = log_ranking(b2n, bitsize, b2nkwargs)
        self.selection = log_selection(b2n, bitsize, b2nkwargs)
        self.value = log_value(b2n, bitsize, b2nkwargs)

        self.add_logs = []

        # Used methods
        self.select: Callable = select
        self.cross: Callable = cross
        self.mutation: Callable = mutate

        # Used variables
        self.elitism = elitism
        self.savetop = savetop

        # Binary to numerical conversion
        self.b2n = b2n
        self.b2nkwargs = b2nkwargs

        self.logdict = {}

        self.creation = datetime.now()

    def __getitem__(self, item):
        return self.logdict[item]

    def __repr__(self):
        return ""

    def __str__(self):
        return "Log for GA created on %s" % self.creation

    def __copy__(self):
        logcopy = log(self.pop, self.select, self.cross, self.mutation,
                       self.b2n, self.elitism, self.savetop,
                       self.bitsize, self.b2nkwargs)

        logcopy.creation = self.creation

        logcopy.time.data = self.time.data
        logcopy.time.epoch = self.time.epoch

        logcopy.ranking.data = self.ranking.data
        logcopy.ranking.epoch = self.ranking.epoch
        logcopy.ranking.ranknum = self.ranking.ranknum
        logcopy.ranking.effectivity = self.ranking.effectivity
        logcopy.ranking.distancex = self.ranking.distancex
        logcopy.ranking.distancefx = self.ranking.distancefx
        logcopy.ranking.bestsol = self.ranking.bestsol

        logcopy.value.data = self.value.data
        logcopy.value.epoch = self.value.epoch
        logcopy.value.value = self.value.value
        logcopy.value.numvalue = self.value.numvalue
        logcopy.value.topx = self.value.topx
        return logcopy

    def copy(self):
        return self.__copy__()

    def __add__(self, other: "log_object"):
        setattr(self, other.__class__.__name__, other)
        print(other)
        print("add:", getattr(self, other.__class__.__name__)) # hier gaat fout
        self.add_logs.append(other)
        return self.__copy__()

    def append(self, other):
        return self.__add__(other)

    def sync_logs(self):
        for lg in self.add_logs:
            setattr(self, lg.__class__.__name__, lg.copy())

        return None

class log_object:

    def __init__(self, b2num, bitsize, b2nkwargs, *args, **kwargs):
        self.epoch = []
        self.data = []

        self.bitsize = bitsize
        self.b2n = b2num
        self.b2nkwargs = b2nkwargs

        self.args = args
        self.kwargs = kwargs

    def __getitem__(self, item: int):
        return self.data[item]

    # def __repr__(self):
    #     return str(self.data)

    def __copy__(self):
        object_copy = log_object(self.b2n, self.bitsize, *self.args, **self.kwargs)
        object_copy.data = self.data
        object_copy.epoch = self.epoch
        return object_copy

    def __len__(self):
        return len(self.epoch)

    def copy(self):
        return self.__copy__()

    def savetxt(self, path):

        return None

    def update(self, data, *args):
        self.data.append(data)
        self.epoch.append(len(self.data))
        return None



class log_time(log_object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __copy__(self):
        object_copy = log_time(self.b2n, self.bitsize, *self.args, **self.kwargs)
        object_copy.data = self.data
        object_copy.epoch = self.epoch
        return object_copy

    def plot(self, save_as="", show=True, *args, **kwargs):

        linestyle = "-"
        if "linestyle" in kwargs:
            linestyle = kwargs["linestyle"]
            kwargs["linestyle"].pop()

        marker = "o"
        if "marker" in kwargs:
            marker = kwargs["marker"]
            kwargs["marker"].pop()

        kwargs["x_label"] = "epoch"
        kwargs["y_label"] = "time"

        kwargs["data_label"] = "avg per epoch: %s s" % (sum(np.array(self.data)[1:] - np.array(self.data)[:-1]) / len(self.data))

        pl = Default(self.epoch, self.data, *args, linestyle=linestyle, marker=marker, **kwargs)

        plt.title("Time: %s s" % self.data[-1])

        if show:
            if save_as != "":
                pl.save_as = save_as
            pl()

        return pl



class log_selection(log_object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.probabilty = []
        self.fitness = []

    def __copy__(self):
        object_copy = log_selection(self.b2n, self.bitsize, self.b2nkwargs, *self.args, **self.kwargs)
        object_copy.data = self.data
        object_copy.epoch = self.epoch
        object_copy.probabilty = self.probabilty
        object_copy.fitness = self.fitness
        return object_copy

    def update(self, data, *args):
        self.data.append(data)
        self.epoch.append(len(self.data))
        self.probabilty.append(args[0])
        self.fitness.append(args[1])
        return None

    def __getitem__(self, item):
        return self.fitness[item]

    def plot(self, top: int = None, show: bool = True, save_as: str = "",**kwargs):
        if top == None:
            top = len(self.data[0])

        avgpepoch = [np.average(i[:top]) for i in self.fitness]

        # plt.plot(self.epoch, avgpepoch, linestyle="-", marker="o", label="Fitness")
        #
        # plt.ylabel("Fitness coefficient")
        # plt.xlabel("Epochs")
        #
        # plt.grid()
        #
        # plt.legend()
        # plt.show()

        pl = Default(self.epoch, avgpepoch, linestyle="-", marker="o", **kwargs)
        if show:
            if save_as != "":
                pl.save_as = save_as
            pl()

        return pl

class log_ranking(log_object):

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ranknum = []
        self.effectivity = []
        self.distancex = []
        self.distancefx = []
        self.bestsol = []

    def __copy__(self):
        object_copy = log_ranking(self.b2n, self.bitsize, *self.args, **self.kwargs)
        object_copy.data = self.data
        object_copy.epoch = self.epoch
        object_copy.ranknum = self.ranknum
        object_copy.effectivity = self.effectivity
        object_copy.distancex = self.distancex
        object_copy.bestsol = self.bestsol
        return object_copy

    def update(self, data, *args):
        """

        :param data:
        :param args: fx, the optimum, highest effectivity[x coordinates, fx]

        :return:
        """
        self.data.append(data)
        self.epoch.append(len(self.data))
        self.fx = args[0]

        if "bitsize" not in self.b2nkwargs:
            self.b2nkwargs["bitsize"] = self.bitsize

        self.ranknum.append(self.b2n(data, **self.b2nkwargs))

        # Calculate the euclidian distance between the optimum and all pop values
        self.distancex.append(np.apply_along_axis(pythagoras, 1, (np.absolute(self.ranknum[-1] - args[1]))**2))
        self.distancefx.append(self.fx - args[2])

        # Determine the effectivity relative to the largest distcance after the first epoch.
        self.effectivity.append(1 - self.distancex[-1] / max(self.distancex[0]))

        # Find the best solution of this iteration and append it to the list
        ind = np.where(self.effectivity[-1] == max(self.effectivity[-1]))[0]
        self.bestsol.append(self.ranknum[-1][ind])

    def __getitem__(self, item: int):
        return self.ranknum[item]

    def __repr__(self):
        return str(self.ranknum)

    def plot(self, top: int = None, show: bool = True, save_as: str = ""
             , datasource = None, **kwargs):

        if top == None:
            top = len(self.effectivity[0])

        if datasource == None:
            datasource = self.distancefx

        elif datasource == self.bestsol:
            pass

        avgpepoch = [np.average(i[0:]) for i in datasource]
        print(avgpepoch)

        if not "linestyle" in kwargs:
            kwargs["linestyle"] = "-"

        if not "marker" in kwargs:
            kwargs["marker"] = "o"

        print(len(self.epoch), len(avgpepoch))

        pl = Default(self.epoch, avgpepoch, **kwargs)
        if show:
            if save_as != "":
                pl.save_as = save_as
            pl()
        return pl


class log_value(log_object):

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = []
        self.numvalue = []
        self.topx = []

    def __getitem__(self, item):
        return self.numvalue[item]

    def __repr__(self):
        return str(self.value)

    def __copy__(self):
        object_copy = log_value(self.b2n, self.bitsize, *self.args, **self.kwargs)
        object_copy.data = self.data
        object_copy.epoch = self.epoch
        object_copy.value = self.value
        object_copy.numvalue = self.numvalue
        object_copy.topx = self.topx
        return object_copy

    def update(self, data, *args):
        self.value.append(data)
        self.epoch.append(len(self.data))

        if "bitsize" not in self.b2nkwargs:
            self.b2nkwargs["bitsize"] = self.bitsize

        self.numvalue.append(np.asarray(convertpop2n(bit2num=self.b2n,
                                                     target=list(data),
                                                     **self.b2nkwargs))[:, 0])
        self.topx.append(args[0])
        return None

    def topvalue(self, item = None):
        """

        :param item:
        :return:
        """
        if item == None:
            return self.topx
        else:
            return self.topx[item]

    def numerical(self, item = None):
        """

        :param item:
        :return:
        """
        if item == None:
            return self.numvalue
        else:
            return self.numvalue[item]

    def plot1d(self, tfx, low, high, save_as="", epoch=0):
        plt.figure()

        plt.plot(self.numvalue[epoch][:, 0], tfx(self.numvalue[epoch][:, 0]),
                 linestyle="",
                 marker="o", label="Algortithm")

        linsp = np.linspace(low, high)
        plt.plot(linsp, tfx(linsp), label="tfx", linestyle="--")

        plt.xlim(low, high)
        plt.ylim(low, high)

        plt.legend(loc="upper right")
        plt.colorbar()

        plt.tight_layout()

        if save_as == "":
            plt.show()
            return None

        plt.savefig(save_as, dpi=600)

        return None

    def plot2d(self, tfx, low, high, save_as="", epoch=0):
        """

        :param tfx:
        :param low:
        :param high:
        :param save_as:
        :param epoch:
        :return:
        """
        plt.figure()

        plt.plot(self.numvalue[epoch][:, 0], self.numvalue[epoch][:, 1],
                         linestyle="",
                         marker="o", label="Algortithm")

        x1, x2 = np.linspace(low, high, 1000), np.linspace(low, high, 1000)
        X1, X2 = np.meshgrid(x1, x2)
        y = tfx([X1, X2])

        plt.pcolormesh(X1, X2, y, cmap='RdBu', shading="auto")

        plt.xlim(low, high)
        plt.ylim(low, high)

        plt.legend(loc="upper right")
        plt.colorbar()

        plt.tight_layout()

        if save_as == "":
            plt.show()
            return None

        plt.savefig(save_as, dpi=600)

        return None

    # Save a gif of all epochs
    def animate1d(self, tfx: Callable, low: int, high: int, save_as=""):
        """

        :param tfx:
        :param low:
        :param high:
        :param save_as:
        :return:
        """

        figure = plt.figure()

        line, = plt.plot(self.numvalue[0][:, 0], tfx(self.numvalue[0][:, 0]),
                         linestyle="",
                         marker="o", label="Algortithm")

        linsp = np.linspace(low, high)
        plt.plot(linsp, tfx(linsp), label="tfx", linestyle="--")

        plt.xlim(low, high)
        plt.ylim(low, high)

        plt.legend(loc="upper right")

        def update(frame):
            print(frame)
            line.set_data(self.numvalue[frame][:, 0], tfx(self.numvalue[frame][:, 0]))

            plt.title("Iteration: %s" % frame)
            return None

        animation = FuncAnimation(figure, update, interval=500,
                                  frames=range(len(self.epoch)))

        if save_as == "":
            plt.show()
            return None

        animation.save(save_as, dpi=600, writer=PillowWriter(fps=1))

        return None

    def animate2d(self, tfx: Callable, low: int, high: int, save_as="", epochs=0,
                  fitness=None):
        """

        :param tfx:
        :param low:
        :param high:
        :param save_as:
        :return:
        """

        figure, [axis1, axis2] = plt.subplots(1, 2)

        line2data = np.array(fitness)
        if fitness==None:
            line2data = self.numvalue

        line, = axis1.plot(self.numvalue[0][:, 0], self.numvalue[0][:, 1],
                         linestyle="",
                         marker="o", label="Algortithm")

        line2 = axis2.bar(range(len(np.sort(line2data[0, :]))), np.sort(line2data[0, :]))

        x1, x2 = np.linspace(low, high, 1000), np.linspace(low, high, 1000)
        X1, X2 = np.meshgrid(x1, x2)
        y = tfx([X1, X2])

        pcmesh = axis1.pcolormesh(X1, X2, y, cmap='RdBu', shading="auto")

        axis1.set_xlim(low, high)
        axis1.set_ylim(low, high)

        axis1.legend(loc="upper right")

        divider = make_axes_locatable(axis1)
        cax = divider.append_axes('right', size='5%', pad=0.05)

        figure.colorbar(pcmesh, cax=cax, orientation='vertical')

        def update(frame):
            print(frame)
            line.set_data(self.numvalue[frame][:, 0], self.numvalue[frame][:, 1])

            sorted_fitness = np.sort(line2data[frame, :])

            for i, b in enumerate(line2):
                b.set_height(sorted_fitness[i])


            axis1.set_title("2D plot")
            axis2.set_title("fitness of individuals")
            plt.title("Iteration: %s" % frame)
            return None

        if epochs == 0:
            epochs = range(len(self.epoch))

        animation = FuncAnimation(figure, update, interval=500,
                                  frames=epochs)

        if save_as == "":
            plt.show()
            return None

        animation.save(save_as, dpi=600, writer=PillowWriter(fps=1))

        return None

if __name__ == "__main__":
    pass


