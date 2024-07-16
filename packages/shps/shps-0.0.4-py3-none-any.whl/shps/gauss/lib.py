import ctypes
import ctypes
from ctypes import c_double, c_int, c_bool, CFUNCTYPE, POINTER
import numpy as np
from numpy.ctypeslib import ndpointer


libfile = str(next(pathlib.Path(__file__).parents[0].glob("libgauss.*"+so_ext)))
lib = ctypes.cdll.LoadLibrary(libfile)

def chebyshev(n):
    pass

