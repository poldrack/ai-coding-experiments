# Create code in python to perform a simulation that repeatedly generates samples of random variates from 6 different distributions (normal, uniform, chi-squared, poisson, exponential, and beta) and computes the mean of each sample, saving it for later use. Then, generate a figure that shows the distribution of the means for each of the distributions.
# - please put each histogram of the means in a different panel in the figure

import numpy as np
import matplotlib.pyplot as plt

# Number of samples and sample size
num_samples = 1000
sample_size = 100

# Initialize arrays to store the means
normal_means = []
uniform_means = []
chi_squared_means = []
poisson_means = []
exponential_means = []
beta_means = []

# Generate samples and compute means
for _ in range(num_samples):
    normal_sample = np.random.normal(loc=0, scale=1, size=sample_size)
    normal_means.append(np.mean(normal_sample))

    uniform_sample = np.random.uniform(low=0, high=1, size=sample_size)
    uniform_means.append(np.mean(uniform_sample))

    chi_squared_sample = np.random.chisquare(df=2, size=sample_size)
    chi_squared_means.append(np.mean(chi_squared_sample))

    poisson_sample = np.random.poisson(lam=5, size=sample_size)
    poisson_means.append(np.mean(poisson_sample))

    exponential_sample = np.random.exponential(scale=1, size=sample_size)
    exponential_means.append(np.mean(exponential_sample))

    beta_sample = np.random.beta(a=2, b=5, size=sample_size)
    beta_means.append(np.mean(beta_sample))

# Create a figure with histograms of the means in separate panels
fig, axs = plt.subplots(2, 3, figsize=(15, 10), sharex=False)

axs[0, 0].hist(normal_means, bins=20, alpha=0.6, color='blue')
axs[0, 0].set_title('Normal')

axs[0, 1].hist(uniform_means, bins=20, alpha=0.6, color='orange')
axs[0, 1].set_title('Uniform')

axs[0, 2].hist(chi_squared_means, bins=20, alpha=0.6, color='green')
axs[0, 2].set_title('Chi-squared')

axs[1, 0].hist(poisson_means, bins=20, alpha=0.6, color='red')
axs[1, 0].set_title('Poisson')

axs[1, 1].hist(exponential_means, bins=20, alpha=0.6, color='purple')
axs[1, 1].set_title('Exponential')

axs[1, 2].hist(beta_means, bins=20, alpha=0.6, color='brown')
axs[1, 2].set_title('Beta')

# Add labels to the axes
for ax in axs.flat:
    ax.set(xlabel='Mean', ylabel='Frequency')

# Adjust spacing between subplots
plt.subplots_adjust(wspace=0.3, hspace=0.3)

# Show the plot
# plt.show()
plt.savefig('histograms.png')