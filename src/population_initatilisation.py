
import numpy as np

from typing import Union, Iterable
from scipy.stats import cauchy
from helper import *
from src.helper import int2ndbit


def rand_bit_pop(n: int, m: int) -> np.ndarray:
    """
    Generate a random bit population
    :param n: Population size dtype int
    :param m: Bitsize dtype int
    :return: List of random bits with a bit being a ndarray array of 0 and 1.
    """
    return np.array([np.random.randint(0, 2, size=m) for _ in range(n)])


def normalrand_bit_pop_float(n, bitsize, lower, upper):

    pop_float = np.linspace(lower, upper, num=n)
    blist = []
    if bitsize == 32:
        for val in range(pop_float.size):
            blist.append(floatToBinary32(pop_float[val]))
            # tval, tres = pop_float[val], b2sfloat(floatToBinary64(pop_float[val]))[0]
            # try: np.testing.assert_almost_equal(tres, tval )
            # except AssertionError: print("Fail")

    elif bitsize == 64:
        for val in range(pop_float.size):
            blist.append(floatToBinary64(pop_float[val]))
            # tval, tres = pop_float[val], b2dfloat(blist[-1])[0]
            # try: np.testing.assert_almost_equal(tres, tval )
            # except AssertionError: print("Fail")

    else:
        pass
    return np.array(blist)


def cauchyrand_bit_pop_float(shape: Union[Iterable, float], bitsize: int, loc: float,
                             scale: float) -> np.ndarray:
    if isinstance(shape, int):
        shape = (shape, 1)
    elif len(shape) == 1:
        shape = (shape[0], 1)

    size = shape[0] * shape[1]

    pop_float = cauchy.rvs(loc=loc, scale=scale, size=size)
    pop_float = np.array(np.array_split(pop_float, int(size/shape[0])), dtype=float)
    blist = []
    for val in range(pop_float.shape[1]):
        blist.append(float2Ndbit(pop_float[:, val], bitsize))

    return np.array(blist)


def uniform_bit_pop_float(shape: Union[Iterable, float], bitsize: int, low: float,
                             high: float) -> np.ndarray:

    if isinstance(shape, int):
        shape = (shape, 1)
    elif len(shape) == 1:
        shape = (shape[0], 1)

    size = shape[0] * shape[1]

    pop_float = np.random.uniform(low, high, size)
    pop_float = np.array(np.array_split(pop_float, int(size/shape[0])), dtype=float)
    blist = []
    for val in range(pop_float.shape[1]):
        blist.append(float2Ndbit(pop_float[:, val], bitsize))

    return np.array(blist)


def bit8(shape: list, bitsize: int = 8, factor = 1.0, bias = 0.0):

    if isinstance(shape, int):
        shape = (shape, 1)
    elif len(shape) == 1:
        shape = (shape[0], 1)

    shape[1] *= bitsize

    blist = []
    for val in range(shape[0]):
        blist.append(np.random.randint(0, 2, shape[1]))

    return np.array(blist, dtype=np.uint8)

def uniform_bit_pop(shape: Iterable, bitsize: int, lower: float, upper: float,
                    factor: float = 1.0, bias: float = 0.0) -> np.ndarray:
    """
    Generate a uniform bit population
    :param shape: Population size dtype tuple
    :param bitsize: Bitsize dtype int
    :param lower: Lower bound dtype float
    :param upper: Upper bound dtype float
    :return: List of random bits with a bit being a ndarray array of 0 and 1.
    """
    pop_float = np.vstack(np.array_split(np.random.uniform(lower, upper, shape[0] * shape[1]), shape[0]))

    if factor < np.abs(lower) or factor < np.abs(upper):
        factor = np.abs(lower) if np.abs(lower) > np.abs(upper) else np.abs(upper)

    return int2ndbit(pop_float, bitsize, factor=factor, bias=bias)

if __name__ == "__main__":
    print(ndbit2int(uniform_bit_pop([10, 4], 8, 4, 12, factor=10), bitsize=8, factor=10))