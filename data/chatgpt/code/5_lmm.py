import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

def read_and_combine_csvs(file_names):
    data = []
    for file_name in file_names:
        df = pd.read_csv(file_name)
        df['file_name'] = file_name
        data.append(df)
    combined_data = pd.concat(data)
    return combined_data

def linear_mixed_model(data):
    model = smf.mixedlm("rt ~ compatible", data, groups=data["file_name"], re_formula="~compatible")
    result = model.fit()
    print(result.summary())
    return result

def create_test_data(num_files=5, num_rows=100, folder="test_data"):
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    file_names = []
    for i in range(num_files):
        file_name = f"{folder}/test_data_{i}.csv"
        file_names.append(file_name)
        
        rt = np.random.randint(100, 1000, size=num_rows)
        correct = np.random.randint(0, 2, size=num_rows)
        compatible = np.random.choice([0, 1], size=num_rows, replace=True)
        
        data = pd.DataFrame({"rt": rt, "correct": correct, "compatible": compatible})
        data.to_csv(file_name, index=False)
        
    return file_names

def test_function():
    file_names = create_test_data()
    combined_data = read_and_combine_csvs(file_names)
    result = linear_mixed_model(combined_data)
    
test_function()
