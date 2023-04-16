# Generate a python script that performs crossvalidation with feature selection incorrectly performed outside of the crossvalidation loop
# first pass failed with normaly disribted data - asked it to use a different feature selecter

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Load your dataset
data = pd.read_csv("your_data.csv")
X = data.drop("target", axis=1)
y = data["target"]

# Number of features to select
k = 5

selector = SelectKBest(score_func=f_classif, k=k)
X_selected = selector.fit_transform(X, y)

# Initialize k-fold cross-validation
kf = KFold(n_splits=5, shuffle=True, random_state=42)
accuracies = []

# Cross-validation loop
for train_index, test_index in kf.split(X_selected):
    X_train, X_test = X_selected[train_index], X_selected[test_index]
    y_train, y_test = y[train_index], y[test_index]

    # Train and evaluate the model
    model = LogisticRegression(solver='liblinear')
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    accuracies.append(accuracy)

mean_accuracy = np.mean(accuracies)
print(f"Mean accuracy : {mean_accuracy:.2f}")
