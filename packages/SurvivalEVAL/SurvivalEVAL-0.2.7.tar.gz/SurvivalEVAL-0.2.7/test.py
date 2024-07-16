# test multiprocessing on loop and compare with single process
from multiprocessing import Pool
import time
import numpy as np
import pandas as pd
import os

def f(x):
    return x*x

if __name__ == '__main__':
    # single process
    start = time.time()
    for i in range(10000000):
        f(i)
    end = time.time()
    print('single process time: ', end - start)

    # multi process with 2 cores
    start = time.time()
    with Pool(2) as p:
        p.map(f, range(10000000))
    end = time.time()
    print('multi process (2 core) time: ', end - start)
    # multi process with 4 cores
    start = time.time()
    with Pool(4) as p:
        p.map(f, range(10000000))
    end = time.time()
    print('multi process (4 core) time: ', end - start)
    # multi process with 8 cores
    start = time.time()
    with Pool(8) as p:
        p.map(f, range(10000000))
    end = time.time()
    print('multi process (8 core) time: ', end - start)
    # multi process with 16 cores
    start = time.time()
    with Pool(16) as p:
        p.map(f, range(10000000))
    end = time.time()
    print('multi process (16 core) time: ', end - start)
    # multi process with 32 cores
    start = time.time()
    with Pool(32) as p:
        p.map(f, range(10000000))
    end = time.time()
    print('multi process (32 core) time: ', end - start)

