# create a simulation to demonstrate the use of randomization to obtain a null distribution for hypothesis testing.  First, generate a bivariate dataset with a sample size of 100 and a correlation of 0.1 between the two variables. Compute the correlation coefficient and obtain a p-value against the null hypothesis of r=0.  Then, randomly shuffle one of the variables 5000 times and compute the correlation each time.  Compute an empirical p-value for  the actual R value based on the null distribution.

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

def generate_bivariate_data(sample_size, corr):
    np.random.seed(42)
    mean = [0, 0]
    cov = [[1, corr], [corr, 1]]
    x, y = np.random.multivariate_normal(mean, cov, sample_size).T
    return x, y

def compute_correlation(x, y):
    corr, p_value = stats.pearsonr(x, y)
    return corr, p_value

def perform_randomization(x, y, n_permutations):
    random_corrs = []

    for _ in range(n_permutations):
        shuffled_y = np.random.permutation(y)
        random_corr, _ = stats.pearsonr(x, shuffled_y)
        random_corrs.append(random_corr)

    return np.array(random_corrs)

def compute_empirical_p_value(actual_corr, random_corrs):
    empirical_p_value = np.mean(np.abs(random_corrs) >= np.abs(actual_corr))
    return empirical_p_value

if __name__ == "__main__":
    sample_size = 100
    corr = 0.1
    n_permutations = 5000

    x, y = generate_bivariate_data(sample_size, corr)
    actual_corr, actual_p_value = compute_correlation(x, y)
    random_corrs = perform_randomization(x, y, n_permutations)
    empirical_p_value = compute_empirical_p_value(actual_corr, random_corrs)

    print(f"Actual correlation: {actual_corr}")
    print(f"Actual p-value: {actual_p_value}")
    print(f"Empirical p-value: {empirical_p_value}")
