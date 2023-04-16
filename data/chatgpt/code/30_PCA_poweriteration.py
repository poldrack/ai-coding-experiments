# generate a class in the scikit-learn style to perform principal component analysis using the power iteration method.  the algorithm should be coded from scratch rather than using an external library.
# create an additional function to compare the results of this method to those of the standard PCA function in scikit-learn

import numpy as np
from scipy.linalg import orth
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler


class PowerIterationPCA:
    def __init__(self, n_components=2, max_iter=1000, tol=1e-6):
        self.n_components = n_components
        self.max_iter = max_iter
        self.tol = tol
        self.components_ = None

    def fit(self, X):
        X = X - np.mean(X, axis=0)
        n_features = X.shape[1]
        self.components_ = np.zeros((self.n_components, n_features))

        for k in range(self.n_components):
            v = np.random.rand(n_features)
            for _ in range(self.max_iter):
                v_new = X.T @ (X @ v)
                v_new /= np.linalg.norm(v_new)

                if np.linalg.norm(v - v_new) < self.tol:
                    break

                v = v_new

            X = X - (X @ v[:, None]) @ v[None, :]
            self.components_[k, :] = v

        return self

    def transform(self, X):
        if self.components_ is None:
            raise ValueError("Fit the model before transforming the data.")

        X = X - np.mean(X, axis=0)
        return X @ self.components_.T

    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)


def compare_pca_results(X, n_components=2):
    # Standardize the data
    scaler = StandardScaler()
    X_std = scaler.fit_transform(X)

    # Apply the custom PowerIterationPCA
    power_iteration_pca = PowerIterationPCA(n_components=n_components)
    X_power_iteration = power_iteration_pca.fit_transform(X_std)

    # Apply the standard PCA from scikit-learn
    sklearn_pca = PCA(n_components=n_components)
    X_sklearn = sklearn_pca.fit_transform(X_std)

    # Visualize the results using scatter plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    ax1.scatter(X_power_iteration[:, 0], X_power_iteration[:, 1], alpha=0.7)
    ax1.set_title("Power Iteration PCA")
    ax1.set_xlabel("PC1")
    ax1.set_ylabel("PC2")

    ax2.scatter(X_sklearn[:, 0], X_sklearn[:, 1], alpha=0.7)
    ax2.set_title("Scikit-learn PCA")
    ax2.set_xlabel("PC1")
    ax2.set_ylabel("PC2")

    plt.show()


if __name__ == "__main__":

    data = load_iris()
    X = data.data
    compare_pca_results(X)
