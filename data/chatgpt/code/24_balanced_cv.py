# create a new crossvalidation class that implements balanced cross-validation for regression that follows the scikit-learn class structure for crossvalidation objects.  this requires finding a set of splits that vary minimally in their distributions, which can be assessed using an F statistic.  
# there is an error in the class, on the command "if split not in balanced_splits:" ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()
# Something seems wrong with the logic of this class, as the class seems to get stuck in an infinite loop during execution.
# "You're right. The issue is caused by the loop used to find the balanced splits. The current implementation can result in an infinite loop if the same split is selected repeatedly. We can fix this by changing the logic for selecting the balanced splits. We can generate all possible splits and then select the n_splits splits with the lowest F-statistics. "

import numpy as np
from scipy import stats
from sklearn.model_selection import KFold
from sklearn.utils import check_random_state, check_array
from sklearn.datasets import make_regression
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score


import numpy as np
from scipy import stats
from sklearn.model_selection import KFold
from sklearn.utils import check_random_state, check_array


class BalancedRegressionCV:
    def __init__(self, n_splits=5, shuffle=True, random_state=None):
        self.n_splits = n_splits
        self.shuffle = shuffle
        self.random_state = random_state

    def _compute_f_statistic(self, y, y_subset):
        n1 = len(y_subset)
        n2 = len(y) - n1

        mean1 = np.mean(y_subset)
        mean2 = np.mean([i for i in y if i not in y_subset])

        sum_of_squares1 = np.sum([(i - mean1) ** 2 for i in y_subset])
        sum_of_squares2 = np.sum([(i - mean2) ** 2 for i in y if i not in y_subset])

        var1 = sum_of_squares1 / (n1 - 1)
        var2 = sum_of_squares2 / (n2 - 1)

        if var2 == 0:
            return np.inf

        return var1 / var2

    def _generate_splits_with_f_statistics(self, y, kf):
        split_f_statistics = []

        for train_index, test_index in kf.split(y):
            y_test = y[test_index]
            f_statistic = self._compute_f_statistic(y, y_test)
            split_f_statistics.append(((tuple(train_index), tuple(test_index)), f_statistic))

        return split_f_statistics

    def _select_balanced_splits(self, split_f_statistics):
        sorted_splits = sorted(split_f_statistics, key=lambda x: x[1])
        return [split for split, _ in sorted_splits[:self.n_splits]]

    def split(self, X, y, groups=None):
        y = check_array(y, ensure_2d=False, dtype=None)
        X = check_array(X, accept_sparse=('csr', 'csc'), dtype=None)
        n_samples = X.shape[0]
        kf = KFold(n_splits=self.n_splits * 2, shuffle=self.shuffle, random_state=self.random_state)

        split_f_statistics = self._generate_splits_with_f_statistics(y, kf)
        balanced_splits = self._select_balanced_splits(split_f_statistics)

        for train_index, test_index in balanced_splits:
            yield np.array(train_index), np.array(test_index)

    def get_n_splits(self, X=None, y=None, groups=None):
        return self.n_splits


# please write another function that generates synthetic data and tests this class 
def test_balanced_regression_cv():
    # Generate synthetic data
    X, y = make_regression(n_samples=200, n_features=10, noise=0.1, random_state=42)

    # Instantiate the BalancedRegressionCV object
    balanced_cv = BalancedRegressionCV(n_splits=5, shuffle=True, random_state=42)

    # Fit a linear regression model and perform cross-validation
    model = LinearRegression()
    scores = cross_val_score(model, X, y, cv=balanced_cv, scoring='neg_mean_squared_error')

    # Print the cross-validation scores and mean score
    print("Balanced Cross-Validation Scores:", scores)
    print("Balanced Cross-Validation Mean Score:", np.mean(scores))

if __name__ == "__main__":
    test_balanced_regression_cv()