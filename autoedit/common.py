import math
import numpy as np

def preprocess(X):
    X[:, 1] = np.maximum(X[:, 1], 400)
    return np.log(X)

def pr(y_hat, y):
    n_pred = sum(y_hat == 1)
    p = 1.0 if n_pred == 0 else sum(y[y_hat == 1] == 1) / n_pred
    r = sum(y_hat[y == 1] == 1) / sum(y == 1)
    return (p, r)

def convolve_left(a, b):
    full = np.convolve(a, b, mode='full')
    offset = math.ceil((full.size - len(a)) / 2)
    return full[offset:(offset + len(a))]