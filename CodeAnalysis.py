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

# %% tags=[]

def summarize_cyclomatic_complexity(cc):
    if cc is None:
        return None
    results = {k: 0 for k in ['mean_cyccomp', 'function', 'class', 'method']}
    complexity = 0
    for v in cc:
        results[v['type']] += 1
        results['mean_cyccomp'] += v['complexity']
    results['mean_cyccomp'] =  results['mean_cyccomp'] / len(cc)
    return results

# %% tags=[]

def get_metrics_df(pickle_file, origin):
    with open(pickle_file, 'rb') as f:
        metrics = pickle.load(f)

    print(f'Number of files: {len(metrics)}')

    allresults = []
    raw_keys = ['loc', 'sloc', 'lloc', 'comments']
    cc_keys = ['mean_cyccomp', 'function', 'class', 'method']
    halstead_keys = ['difficulty', 'bugs']
    for k, v in metrics.items():
        # skip if errors
        error = False
        for kk, vv in v.items():
            if 'error' in vv:
                error = True
        if error:
            print(f'Error in {k}, skipping')
            continue

        fileresults = [k, origin]
        
        # flake8
        fileresults.append(len(v['flake8']))
        
        # raw_metrics
        fileresults.extend(v['raw_metrics'][kk] for kk in raw_keys)

        # cyclomatic_complexity
        cc_summary = summarize_cyclomatic_complexity(
                v['cyclomatic_complexity']
            )
        fileresults.extend([cc_summary[kk] for kk in cc_keys])

        # maintainability_index
        fileresults.append(v['maintainability_index']['mi'])

        # halstead_metrics
        fileresults.extend(
            v['halstead_complexity']['total'][kk] for kk in halstead_keys)

        allresults.append(fileresults)

    return pd.DataFrame(allresults, 
                    columns=['file', 'origin', 'flake8'] + raw_keys  + cc_keys +\
                        ['mi']+ halstead_keys)
                        

df_chatgpt = get_metrics_df('metrics_chatgpt_code.pickle', 'chatgpt')
df_github = get_metrics_df('metrics_github_code.pickle', 'github')

df = pd.concat([df_chatgpt, df_github])
df.reset_index(inplace=True)
del df['index']

# %%

sns.displot(df, x='mi', hue='origin', kind='kde', fill=True)
print(df.groupby('origin')['mi'].describe())
ttest_ind(df[df['origin'] == 'chatgpt']['mi'], df[df['origin'] == 'github']['mi'])
# %%
sns.displot(df, x='bugs', hue='origin', kind='kde', fill=True)
print(df.groupby('origin')['bugs'].describe())
ttest_ind(df[df['origin'] == 'chatgpt']['bugs'], df[df['origin'] == 'github']['bugs'])

# %%

df['flake8_per_loc'] = df['flake8'] / df['loc']
sns.displot(df, x='flake8_per_loc', hue='origin', kind='kde', fill=True)
print(df.groupby('origin')['flake8_per_loc'].describe())
ttest_ind(df[df['origin'] == 'chatgpt']['flake8_per_loc'], df[df['origin'] == 'github']['flake8_per_loc'])


# %%

sns.displot(df, x='mean_cyccomp', hue='origin', kind='kde', fill=True)
print(df.groupby('origin')['mean_cyccomp'].describe())
ttest_ind(df[df['origin'] == 'chatgpt']['mean_cyccomp'], df[df['origin'] == 'github']['mean_cyccomp'])

# %%
sns.displot(df, x='difficulty', hue='origin', kind='kde', fill=True)
print(df.groupby('origin')['difficulty'].describe())
ttest_ind(df[df['origin'] == 'chatgpt']['difficulty'], df[df['origin'] == 'github']['difficulty'])
# %%
