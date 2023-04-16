# please create a python class that implements the PC causal inference algorithm. 
# please code the algorithm from scratch rather than using an existing library.
# please recode the independence test using partial correlation.  
# please create a synthetic test dataset for testing the usage
# please create a function to generate a synthetic dataset with simple causal structure

import pandas as pd
import numpy as np
import itertools
from scipy import stats

class PCCausalInference:
    def __init__(self, data, alpha=0.05):
        self.data = data
        self.alpha = alpha
        self.adj_matrix = self.initialize_adj_matrix()

    def initialize_adj_matrix(self):
        columns = self.data.columns
        adj_matrix = pd.DataFrame(data=1, index=columns, columns=columns)
        for column in columns:
            adj_matrix.at[column, column] = 0
        return adj_matrix

    def partial_corr(self, x, y, z):
        if len(z) == 0:
            corr_matrix = np.corrcoef(self.data[[x, y]].values.T)
            return corr_matrix[0, 1]
        
        corr_matrix = np.corrcoef(self.data[[x, y] + z].values.T)
        inv_corr_matrix_z = np.linalg.inv(corr_matrix[2:, 2:])
        partial_corr_coef = -np.dot(corr_matrix[0, 2:], np.dot(inv_corr_matrix_z, corr_matrix[1, 2:])) / \
                            np.sqrt((1 - np.dot(corr_matrix[0, 2:], np.dot(inv_corr_matrix_z, corr_matrix[0, 2:]))) * \
                                    (1 - np.dot(corr_matrix[1, 2:], np.dot(inv_corr_matrix_z, corr_matrix[1, 2:]))))
        return partial_corr_coef

    def independence_test(self, x, y, z):
        partial_corr_coef = self.partial_corr(x, y, z)
        sample_size = len(self.data)
        t_stat = np.sqrt((sample_size - len(z) - 3) * (1 - partial_corr_coef**2)) * partial_corr_coef
        p_value = 2 * (1 - stats.t.cdf(np.abs(t_stat), df=sample_size - len(z) - 3))
        return p_value > self.alpha

    def get_neighbors(self, variable):
        return self.adj_matrix.index[self.adj_matrix[variable] == 1].tolist()

    def remove_edge(self, x, y):
        self.adj_matrix.at[x, y] = 0
        self.adj_matrix.at[y, x] = 0

    def pc_algorithm(self):
        variables = self.data.columns
        for (x, y) in itertools.combinations(variables, 2):
            for k in range(len(variables) - 2):
                subsets = itertools.combinations(set(variables) - {x, y}, k)
                for subset in subsets:
                    if self.independence_test(x, y, list(subset)):
                        self.remove_edge(x, y)
                        break
        return self.adj_matrix


def generate_synthetic_data(n_samples=1000, a_to_b=2, b_to_c=1.5, noise_level=1, seed=42):
    np.random.seed(seed)

    A = np.random.normal(0, 1, n_samples)
    B = A * a_to_b + np.random.normal(0, noise_level, n_samples)
    C = B * b_to_c + np.random.normal(0, noise_level, n_samples)

    data = pd.DataFrame({'A': A, 'B': B, 'C': C})
    return data

data = generate_synthetic_data(n_samples=1000, a_to_b=2, b_to_c=0, noise_level=.5)

pc = PCCausalInference(data)
adj_matrix = pc.pc_algorithm()
print(adj_matrix)