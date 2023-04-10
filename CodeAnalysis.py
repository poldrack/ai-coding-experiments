# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% tags=[]
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from statsmodels.stats.weightstats import ttest_ind
from ttest import t_test_ind_report

# %% tags=[]

df = pd.read_csv(f'code_info_github.csv')
df = pd.concat([df,
                pd.read_csv(f'code_info_chatgpt.csv'),])
df.reset_index(inplace=True)
del df['index']
df = df.dropna()
df['flake8_per_loc'] = df['flake8'] / df['loc']

# %% tags=[]

filter_for_length = True

if filter_for_length:
    min_loc = df.query('origin == "chatgpt"')['loc'].min()
    max_loc = df.query('origin == "chatgpt"')['loc'].max()
    df = df[df['loc'] <= max_loc]
    df = df[df['loc'] >= min_loc]
# %%

for var in [ 'mi', 'bugs', 'difficulty', 'flake8_per_loc', 'mean_cyccomp']:
    print(var)
    print(t_test_ind_report(df[df['origin'] == 'chatgpt'][var],
          df[df['origin'] == 'github'][var]))
    print(df.groupby('origin')[var].describe())
    plt.figure()
    sns.boxplot(x='origin', y=var, data=df)
    plt.savefig(f'../images/{var}_boxplot.png')
    plt.figure()
    sns.displot(df, x=var, hue='origin', kind='kde', fill=True)
    plt.savefig(f'../images/{var}_kde.png')

# %%
