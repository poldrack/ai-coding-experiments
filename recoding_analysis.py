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
# analyses of AI recoding

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import re
from scipy import stats
from statsmodels.stats.multitest import multipletests

# %% tags=[]
# load data

df_gpt4 = pd.read_csv('analysis_outputs/code_info_gpt4.csv',
                      index_col=0)
df_gpt4['origin'] = 'gpt4'

df_orig = pd.read_csv('analysis_outputs/code_info_github_filt-gpt4.csv',
                      index_col=0)
df_orig['origin'] = 'github'

assert set(df_gpt4.filename) == set(df_orig.filename)

df_gpt3 = pd.read_csv('analysis_outputs/code_info_gpt3.csv',
                      index_col=0)
df_gpt3['origin'] = 'gpt3'


df = pd.concat([df_gpt4, df_orig, df_gpt3])
del df['github_license']
del df['github_commit']


df_wide = df_orig.merge(df_recoded, on='filename', 
                        suffixes=['_orig', '_gpt4'])
df_wide = df_orig.merge(df_recoded, on='filename', 
                        suffixes=['', '_gpt3'])


# %% tags=[]

vars_to_drop = ['filename', 'autogen', 'obfuscations',
                'flake8_nsyntaxerrors']

summary_df = df.drop(vars_to_drop, axis=1).groupby('origin').mean().T

# %%

# for each variable, do a t-test to see if the means are different
# between the original and recoded versions

for var in summary_df.index:
    if var in ['filename', 'origin',
               'github_license', 'github_commit']:
        continue
    ttresult = stats.ttest_ind(df_wide[var + '_orig'],
                          df_wide[var + '_recoded'])
    summary_df.loc[var, 't'] = ttresult.statistic
    summary_df.loc[var, 'p'] = ttresult.pvalue
summary_df['p_fdr'] = multipletests(
    summary_df.p, method='fdr_bh')[1]

print(summary_df.query('p_fdr < 0.05'))
# %%
