import argparse
import common
import numpy as np
import pickle
import scipy.optimize

from sklearn import svm

DEFAULT_MIN_SUPPORT = 5

parser = argparse.ArgumentParser(description='Evaluate video using a trained model.')
parser.add_argument('input', type=str, help='Path to the input features.')
parser.add_argument('model', type=str, help='Model for feature evaluation.')
parser.add_argument('output', type=str, help='Path for the output evaluation.')
parser.add_argument('--has_truth', type=bool, default=False, help='Whether the features include group truth.')
parser.add_argument('--min_support', type=int, default=DEFAULT_MIN_SUPPORT, help='Minimum support for cut smoothing.')

def evaluate(X, model, min_support=DEFAULT_MIN_SUPPORT):
    y_hat = model['model'].predict(common.preprocess(X)) > model['thresh']
    return common.convolve_left(y_hat, np.ones(10).astype(np.uint8)) > min_support

def main():
    args = parser.parse_args()
    data = np.loadtxt(args.input, delimiter=',')
    t = data[:, 0]
    if args.has_truth:
        X = data[:, 1:-1]
        y = data[:, -1].astype(np.uint8)
    else:
        X = data[:, 1:]
        y = None
    
    with open(args.model, 'rb') as model_file:
        model = pickle.load(model_file)

    y_hat = evaluate(X, model, args.min_support)
    
    if y is not None:
        p, r = common.pr(y_hat, y)
        print('Threshold = %f' % model['thresh'])
        print('  p = %f' % p)
        print('  r = %f' % r)

    np.savetxt(args.output, np.stack([t, y_hat], axis=1), delimiter=',', fmt='%.18g')

if __name__ == '__main__':
    main()