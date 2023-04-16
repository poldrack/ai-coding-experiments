# create a simulation in python that generates a version of the "corridor of stability" plot by Felix Schonbrodt.  The plot should show how correlation estimates become less variable as the sample size increases.
# This plot is not exactly right.  It should show how the correlation changes for each sample as the sample is incrementally increased.  it should show this line for each of the samples.
# This is not exactly right; the line for each sample should extend all the way to the maximum sample size.
# -- still not exactly right but close enough
# please rewrite this code putting each component into a separate function

import numpy as np
import matplotlib.pyplot as plt


def generate_data(n, true_corr, noise_sd):
    """
    Generate n pairs of random normal variables with correlation true_corr and
    independent noise with standard deviation noise_sd.
    """
    x = np.random.normal(size=n)
    y = true_corr * x + np.random.normal(scale=noise_sd, size=n)
    return x, y


def compute_correlations(x, y):
    """
    Compute the correlations for each sample size from 1 to n.
    """
    n = len(x)
    corrs = np.zeros(n)
    for i in range(n):
        corrs[i] = np.corrcoef(x[:i+1], y[:i+1])[0, 1]
    return corrs


def fill_in_correlations(corrs):
    """
    Fill in the remaining correlation values with the final correlation estimate.
    """
    n = len(corrs)
    corrs[n-1:] = corrs[n-1]
    return corrs


def plot_corridor_of_stability(sample_sizes, corrs):
    """
    Plot the correlations for each sample size as a gray line that extends to the
    maximum sample size.
    """
    plt.plot(range(1, len(corrs)+1), corrs, color='gray', alpha=0.5)
    plt.xlabel('Sample size')
    plt.ylabel('Correlation estimate')
    plt.title('Corridor of stability plot')
    plt.show()


def simulate_corridor_of_stability(min_size, max_size, step_size, true_corr, noise_sd):
    """
    Generate data with the given parameters for each sample size from min_size to
    max_size in steps of step_size. Compute the correlations for each sample size
    and fill in the remaining correlation values with the final correlation estimate.
    Plot the correlations for each sample size as a gray line that extends to the
    maximum sample size.
    """
    sample_sizes = np.arange(min_size, max_size + step_size, step_size)
    corrs = np.zeros((len(sample_sizes), max_size))
    for i, n in enumerate(sample_sizes):
        x, y = generate_data(max_size, true_corr, noise_sd)
        corrs[i, :n] = compute_correlations(x[:n], y[:n])
        corrs[i, :] = fill_in_correlations(corrs[i, :])
    plot_corridor_of_stability(sample_sizes, corrs)


# Example usage
simulate_corridor_of_stability(5, 100, 5, 0.5, 1.0)
