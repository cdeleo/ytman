import common

import argparse
import numpy as np
import pickle
import scipy.optimize

from sklearn import svm

N_THRESH = 100

parser = argparse.ArgumentParser(description='Train a model for identifying clip points.')
parser.add_argument('input', type=str, help='Path to the input features.')
parser.add_argument('output', type=str, help='Path for the output model.')
parser.add_argument('--recall', type=float, default=0.9, help='Target recall for the model.')
args = parser.parse_args()

def main():
    data = np.loadtxt(args.input, delimiter=',')
    X = data[:, 1:-1]
    y = data[:, -1].astype(np.uint8)

    svc = svm.SVC(class_weight='balanced')
    svc.fit(X, y)
    df = svc.decision_function(X)

    res = scipy.optimize.minimize_scalar(
        lambda thresh: (common.pr(df > thresh, y)[1] - args.recall) ** 2,
        bounds=(min(df), max(df)))
    if not res.success:
        raise Exception(res.message)
    thresh = res.x

    p, r = common.pr(df > thresh, y)
    print('Threshold = %f' % thresh)
    print('  p = %f' % p)
    print('  r = %f' % r)

    with open(args.output, 'wb') as output_file:
        pickle.dump({
            'svc': svc,
            'thresh': thresh,
        }, output_file)

if __name__ == '__main__':
    main()