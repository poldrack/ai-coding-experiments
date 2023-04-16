# generate a python class that fits hurdle regression model, with a scikit-learn type interface.
# The continuous model should use a regression moethod taht is appropriate for counts
# the load_boston function is no longer available in scikit-learn.  please use a newer dataset
# that dataset does not include any zeros in the outcome. please use an example dataset that includes zero in the outcome.

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.linear_model import LogisticRegression, PoissonRegressor
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error


class HurdleRegression(BaseEstimator, RegressorMixin):
    def __init__(self, binary_model=None, continuous_model=None):
        self.binary_model = binary_model if binary_model is not None else LogisticRegression()
        self.continuous_model = continuous_model if continuous_model is not None else PoissonRegressor()

    def fit(self, X, y):
        # Fit the binary model on the whole dataset
        binary_y = (y > 0).astype(int)
        self.binary_model.fit(X, binary_y)

        # Fit the continuous model only on non-zero outcomes
        continuous_X = X[binary_y == 1]
        continuous_y = y[binary_y == 1]
        self.continuous_model.fit(continuous_X, continuous_y)

        return self

    def predict(self, X):
        # Predict the probability of non-zero outcome
        prob_non_zero = self.binary_model.predict_proba(X)[:, 1]

        # Predict the non-zero outcome
        non_zero_pred = self.continuous_model.predict(X)

        # Combine the predictions to obtain the final prediction
        return prob_non_zero * non_zero_pred


# Example usage:
# Load the Abalone dataset
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/abalone/abalone.data"
column_names = [
    "Sex", "Length", "Diameter", "Height", "Whole weight", 
    "Shucked weight", "Viscera weight", "Shell weight", "Rings"
]

data = pd.read_csv(url, names=column_names)

# Preprocess the data
data["Sex"] = LabelEncoder().fit_transform(data["Sex"])
X = data.drop("Rings", axis=1).values
y = data["Rings"].values

# Convert some of the positive outcomes to zero to create a dataset with zeros in the outcome
y_zero_mask = (y >= 1) & (y <= 3)
y[y_zero_mask] = 0

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Fit the Hurdle Regression model
model = HurdleRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)

print("Mean squared error:", mean_squared_error(y_test, predictions))
