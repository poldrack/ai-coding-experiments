#Create python code that generates a new class called LinearRegressionStats which extends sklearn.linear_model.LinearRegression() to compute the t statistic and p-value for each regressor in the model.
#
#- first try used a dataset no longer included in sklearn
#- second try fixed that problem but generated a runtime error: RuntimeError: scikit-learn estimators should always specify their parameters in the signature of their __init__ (no varargs). <class '__main__.LinearRegressionStats'> with constructor (self, *args, **kwargs) doesn't  follow this convention.
#- third try gave error: __init__() got an unexpected keyword argument 'normalize' (that argument appears to have been deprecated according to chatgpt)
#- ran correctly on fourth try


import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.datasets import load_diabetes

class LinearRegressionStats(LinearRegression):
    def __init__(self, fit_intercept=True, copy_X=True, n_jobs=None, positive=False):
        super().__init__(fit_intercept=fit_intercept, copy_X=copy_X, n_jobs=n_jobs, positive=positive)
        self.t_statistics_ = None
        self.p_values_ = None

    def fit(self, X, y, *args, **kwargs):
        super().fit(X, y, *args, **kwargs)
        self._compute_t_statistics_and_p_values(X, y)

    def _compute_t_statistics_and_p_values(self, X, y):
        predictions = self.predict(X)
        errors = y - predictions

        X = np.asarray(X)
        y = np.asarray(y)

        # Compute the standard error of the estimates
        residual_sum_of_squares = np.sum(errors**2)
        degrees_of_freedom = X.shape[0] - X.shape[1] - 1
        sigma_squared = residual_sum_of_squares / degrees_of_freedom
        X_squared = np.sum(X**2, axis=0)

        standard_errors = np.sqrt(sigma_squared / X_squared)

        # Compute the t-statistics
        self.t_statistics_ = self.coef_ / standard_errors

        # Compute the p-values
        self.p_values_ = 2 * (1 - stats.t.cdf(np.abs(self.t_statistics_), degrees_of_freedom))

# Example usage
if __name__ == "__main__":
    diabetes = load_diabetes()
    X, y = diabetes.data, diabetes.target

    model = LinearRegressionStats()
    model.fit(X, y)

    print("T-statistics:", model.t_statistics_)
    print("P-values:", model.p_values_)
