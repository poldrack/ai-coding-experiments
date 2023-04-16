# please create code to generate some test data for this code (#9)

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification

# Create synthetic test data
n_samples = 1000
n_features = 20
n_informative = 5

X, y = make_classification(n_samples=n_samples, n_features=n_features, n_informative=n_informative, random_state=42)

# Convert the generated data to a pandas DataFrame
feature_names = [f"feature_{i}" for i in range(1, n_features + 1)]
X_df = pd.DataFrame(X, columns=feature_names)
y_df = pd.DataFrame(y, columns=["target"])

# Combine the feature and target DataFrames
data = pd.concat([X_df, y_df], axis=1)

# Save the generated data to a CSV file
data.to_csv("your_data.csv", index=False)
