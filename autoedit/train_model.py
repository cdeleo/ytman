import common

import argparse
import ng3
import numpy as np
import pickle
import scipy.optimize

from matplotlib import pyplot as plt
from sklearn import svm

N_THRESH = 100

parser = argparse.ArgumentParser(description='Train a model for identifying clip points.')
parser.add_argument('input', type=str, help='Path to the input features.')
parser.add_argument('output', type=str, help='Path for the output model.')
parser.add_argument('--recall', type=float, default=0.9, help='Target recall for the model.')
args = parser.parse_args()

def main():
    data = np.loadtxt(args.input, delimiter=',')
    X = common.preprocess(data[:, 1:-1])
    y = data[:, -1].astype(np.uint8)

    model = ng3.Ng3Model()
    model.fit(X, y, monotonicity=[ng3.Ng3Model.NON_INCREASING, ng3.Ng3Model.NON_INCREASING])
    df = model.predict(X)

    for i, model_part in enumerate(model._models):
        plt.figure()
        plt.plot(model_part._xs, model_part._ys)
        plt.title('Feature %d' % i)
        plt.savefig('feature_%d.png' % i)

    xx, yy = np.meshgrid(
        np.linspace(min(X[:, 0]), max(X[:, 0]), 1000),
        np.linspace(min(X[:, 1]), max(X[:, 1]), 1000))
    Z = model.predict(np.hstack([xx.ravel().reshape(-1, 1), yy.ravel().reshape(-1, 1)]))
    Z = Z.reshape(xx.shape)
    plt.figure()
    plt.contourf(xx, yy, Z)
    plt.title('Decision surface')
    plt.savefig('decision.png')
    plt.scatter(X[y==0, 0], X[y==0, 1], c='b', marker='+')
    plt.scatter(X[y==1, 0], X[y==1, 1], c='r', marker='+')
    plt.savefig('decision_with_points.png')

    thresh = np.percentile(df[y == 1], 100 * (1 - args.recall))
    p, r = common.pr(df > thresh, y)
    print('Threshold = %f' % thresh)
    print('  p = %f' % p)
    print('  r = %f' % r)

    with open(args.output, 'wb') as output_file:
        pickle.dump({
            'model': model,
            'thresh': thresh,
        }, output_file)

if __name__ == '__main__':
    main()