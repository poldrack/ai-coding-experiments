# create python code to simulate the effect of overfitting in regression. 1) generate synthetic data with 32 observations for two variables from a bivariate normal distribution with a correlation of 0.5.  2) fit three models to the data: a linear regression model, a 2nd-order polynomial regression model, and a 9-th order polynomial model.  3) Compute the error for each of these models on the synthetic training data, and on a synthetic test dataset generated from the same distribution.  4) plot the fitted lines for each of the fitted models overlaid on the training data.

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error
from scipy.stats import multivariate_normal

def generate_synthetic_data(n, mean, cov):
    data = multivariate_normal(mean, cov).rvs(n)
    X, y = data[:, 0].reshape(-1, 1), data[:, 1]
    return X, y

def fit_models(X, y, degrees):
    models = []
    for degree in degrees:
        if degree == 1:
            model = LinearRegression()
        else:
            model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
        model.fit(X, y)
        models.append(model)
    return models

def compute_errors(models, X_train, y_train, X_test, y_test):
    errors = []
    for model in models:
        train_error = mean_squared_error(y_train, model.predict(X_train))
        test_error = mean_squared_error(y_test, model.predict(X_test))
        errors.append((train_error, test_error))
    return errors

def plot_fitted_lines(models, X_train, y_train, degrees):
    plt.scatter(X_train, y_train, color='b', label='Training data')
    X_range = np.linspace(X_train.min(), X_train.max(), 1000).reshape(-1, 1)

    for model, degree in zip(models, degrees):
        plt.plot(X_range, model.predict(X_range), label=f'{degree}-order polynomial')

    plt.legend()
    plt.xlabel('X')
    plt.ylabel('y')
    plt.title('Fitted lines for polynomial regression models')
    plt.show()

def main():
    np.random.seed(0)
    mean = [0, 0]
    cov = [[1, 0.5], [0.5, 1]]
    n = 32
    degrees = [1, 2, 9]

    X_train, y_train = generate_synthetic_data(n, mean, cov)
    X_test, y_test = generate_synthetic_data(n, mean, cov)

    models = fit_models(X_train, y_train, degrees)
    errors = compute_errors(models, X_train, y_train, X_test, y_test)

    for degree, (train_error, test_error) in zip(degrees, errors):
        print(f'Degree {degree}: Train error = {train_error:.4f}, Test error = {test_error:.4f}')

    plot_fitted_lines(models, X_train, y_train, degrees)

if __name__ == "__main__":
    main()
