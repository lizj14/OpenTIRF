# ---------------------------------------------
# debug.py
# the functions used by times when debugging.
# ---------------------------------------------
import numpy as np
import time


def if_minus_in_nparray(array, info):
    if type(array) is not np.ndarray:
        array = np.array(array)
    print('array to check: %s, %s;' % (info, array.shape))
    search_zero = np.where(array <= 0)
    if len(search_zero[0]) != 0:
        print('zero or minus in %s: %d' % (info, len(search_zero[0])))
        print('min: %s' % np.min(array))
    else:
        print('none zero or minus in %s' % info)


def return_time():
    return time.time()
