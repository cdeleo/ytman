import math
import numpy as np

def pr(y_hat, y):
    p = sum(y[y_hat == 1] == 1) / sum(y_hat == 1)
    r = sum(y_hat[y == 1] == 1) / sum(y == 1)
    return (p, r)

def convolve_left(a, b):
    full = np.convolve(a, b, mode='full')
    offset = math.ceil((full.size - len(a)) / 2)
    return full[offset:(offset + len(a))]