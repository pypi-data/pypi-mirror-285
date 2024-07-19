import pyedflib
from scipy import interpolate
import numpy as np
def clip(arr: np.ndarray, min, max):
    arr = np.round(arr)
    arr = np.clip(arr, min, max)
    return arr



def re_sample(i_data, rate):
    d = i_data
    f = interpolate.interp1d(range(len(d)), d, kind='quadratic')
    tnew = np.linspace(0, len(d) - 1, round(len(d) * rate))
    xnew = f(tnew)
    xnew = clip(xnew, min(i_data), max(i_data))
    return xnew

re_sample(list(range(0,500,10)), 10)