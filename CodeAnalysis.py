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

df_github = pd.read_csv(f'code_info_github.csv', index_col=0)
df_github['origin'] = 'github'

df_chatgpt = pd.read_csv(f'code_info_chatgpt.csv', index_col=0)
df_chatgpt['origin'] = 'chatgpt'

df = pd.concat([df_github, df_chatgpt])
df.reset_index(inplace=True)
del df['index']
df['flake8_messages_per_loc'] = df['flake8_nmessages'] / df['raw_loc']
df['flake8_syntaxerrors_per_loc'] = df['flake8_nsyntaxerrors'] / df['raw_loc']

# %% tags=[]

filter_for_length = True

if filter_for_length:
    min_loc = df.query('origin == "chatgpt"')['raw_loc'].min()
    max_loc = df.query('origin == "chatgpt"')['raw_loc'].max()
    df = df[df['raw_loc'] <= max_loc]
    df = df[df['raw_loc'] >= min_loc]
# %%

for var in [ 'mi_mi', 'hal_bugs', 'hal_difficulty',
            'flake8_messages_per_loc', 'flake8_syntaxerrors_per_loc',
            'mean_cc']:
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
