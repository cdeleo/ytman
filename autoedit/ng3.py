import bisect
import numpy as np
import scipy.optimize
import sklearn.ensemble

class PwlModel(object):

    def __init__(self, points):
        self._xs = []
        self._ys = []
        for p in points:
            self._xs.append(p[0])
            self._ys.append(p[1])

    def eval(self, x):
        i = bisect.bisect(self._xs, x)
        if i == 0:
            return self._ys[0]
        elif i == len(self._ys):
            return self._ys[-1]
        t = (x - self._xs[i - 1]) / (self._xs[i] - self._xs[i - 1])
        return t * (self._ys[i] - self._ys[i - 1]) + self._ys[i - 1]

class Ng3Model(object):

    NON_MONOTONIC = 0
    NON_DECREASING = 1
    NON_INCREASING = 2

    _EVAL_FACTOR = 10

    def __init__(self, max_depth=5, n_segments=5):
        self._max_depth = max_depth
        self._n_segments = n_segments
        self._models = []

    def _eval_forest(self, forest, X):
        X_eval = np.percentile(X, np.linspace(0, 100, self._n_segments * self._EVAL_FACTOR + 1))
        y_eval = forest.predict(X_eval.reshape(-1, 1))
        return X_eval, y_eval

    @staticmethod
    def _delta_encode(x):
        dx = [x[0]]
        for i in range(1, len(x)):
            dx.append(x[i] - x[i - 1])
        return dx

    @staticmethod
    def _delta_decode(dx):
        x = [dx[0]]
        for i in range(1, len(dx)):
            x.append(x[-1] + dx[i])
        return x

    def _fit_pwl(self, x_data, y_data, monotonicity):
        xs = x_data[::self._EVAL_FACTOR]
        if monotonicity == self.NON_MONOTONIC:
            bounds = (-np.inf, np.inf)
            params_0 = self._delta_encode(np.linspace(min(y_data), max(y_data), len(xs)))
        elif monotonicity == self.NON_DECREASING:
            bounds = ([-np.inf] + [0] * self._n_segments, np.inf)
            params_0 = self._delta_encode(np.linspace(min(y_data), max(y_data), len(xs)))
        elif monotonicity == self.NON_INCREASING:
            bounds = (-np.inf, [np.inf] + [0] * self._n_segments)
            params_0 = self._delta_encode(np.linspace(max(y_data), min(y_data), len(xs)))

        def _f(X, *params):
            ys = self._delta_decode(params)
            pwl = PwlModel(zip(xs, ys))
            return [pwl.eval(x) for x in X]
        params_opt, _ = scipy.optimize.curve_fit(_f, x_data, y_data, p0=params_0, bounds=bounds)
        ys_opt = self._delta_decode(params_opt)
        return PwlModel(zip(xs, ys_opt))

    def _fit_forest(self, X, y, monotonicity):
        forest = sklearn.ensemble.RandomForestRegressor(
            max_depth=self._max_depth,
            max_samples=0.5,
            min_samples_leaf=0.05)
        forest.fit(X.reshape(-1, 1), y)
        x_eval, y_eval = self._eval_forest(forest, X)
        return self._fit_pwl(x_eval, y_eval, monotonicity)

    def fit(self, X, y, monotonicity=None):
        if monotonicity is None:
            monotonicity = [self.NON_MONOTONIC] * X.shape[1]

        for i in range(X.shape[1]):
            self._models.append(self._fit_forest(X[:, i], y, monotonicity=monotonicity[i]))

    def predict(self, X):
        z = np.zeros(X.shape[0])
        for i in range(X.shape[0]):
            z[i] = sum(self._models[j].eval(X[i, j]) for j in range(X.shape[1]))
        return z
