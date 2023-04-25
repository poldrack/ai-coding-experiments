
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from statsmodels.stats.weightstats import ttest_ind
from ttest import t_test_ind_report
from scipy.stats import ttest_rel
from pathlib import Path
from statsmodels.stats.multitest import multipletests
import os

def get_metrics_df(basedir):
    if isinstance(basedir, str):
        basedir = Path(basedir)
    df_github = pd.read_csv(basedir /
        f'results/github/code_analytics.csv', index_col=0)
    df_github['origin'] = 'github'
    df_github['flake8_messages_per_loc'] = df_github['flake8_nmessages'] / df_github['raw_loc']
    df_github['flake8_syntaxerrors_per_loc'] = df_github['flake8_nsyntaxerrors'] / df_github['raw_loc']

    df_gpt4 = pd.read_csv(basedir /
        f'results/gpt4/code_analytics.csv', index_col=0)
    df_gpt4['origin'] = 'gpt4'
    df_gpt4['flake8_messages_per_loc'] = df_gpt4['flake8_nmessages'] / df_gpt4['raw_loc']
    df_gpt4['flake8_syntaxerrors_per_loc'] = df_gpt4['flake8_nsyntaxerrors'] / df_gpt4['raw_loc']

    # find filenames that are present in both
    df_wide = pd.merge(df_github, df_gpt4, on='filename', how='inner')

    # filter out any files with syntax errors in gpt4 output

    error_df = df_wide.loc[df_wide.flake8_nsyntaxerrors_y > 0]
    print(f'Filtered out {len(error_df)} files with syntax errors in gpt4 output')
    df_wide = df_wide.loc[df_wide.flake8_nsyntaxerrors_y == 0] 
    print(f'Kept {len(df_wide)} files for full analysis')
    df_wide.to_csv(basedir / 'results/gpt4/combined_code_analytics_wide.csv')

    # find and drop files missing from one or the other data frame
    df_github_mismatch = df_github.loc[
        ~df_github.filename.isin(df_wide.filename)]
    print(f'Github mismatch: {len(df_github_mismatch)}')
    df_gpt4_mismatch = df_gpt4.loc[
        ~df_gpt4.filename.isin(df_wide.filename)]
    print(f'GPT4 mismatch: {len(df_gpt4_mismatch)}')

    df_github = df_github.loc[
        df_github.filename.isin(df_wide.filename)]
    df_gpt4 = df_gpt4.loc[
        df_gpt4.filename.isin(df_wide.filename)]

    df = pd.concat([df_github, df_gpt4])
    df.reset_index(inplace=True)
    del df['index']
    df['flake8_messages_per_loc'] = df['flake8_nmessages'] / df['raw_loc']
    df['flake8_syntaxerrors_per_loc'] = df['flake8_nsyntaxerrors'] / df['raw_loc']
    df.to_csv(basedir / 'results/gpt4/combined_code_analytics.csv')
    return df, df_wide


def plot_var_swarm_plus_line(df, df_wide, var, alpha=1,
                            print_results=False,
                            plot_figure=True, fig=None):
    # drop nas for this var from both subjs
    df_var = df_wide[[f'{var}_x', f'{var}_y', 'filename']].dropna()
    if print_results:
        print(var)
        print(f'dropped {df_wide.shape[0] - df_var.shape[0]} NAs')

    df_var_long = df.loc[df.filename.isin(df_var.filename)]

    tt_result = ttest_rel(df_var[f'{var}_x'], 
                          df_var[f'{var}_y'])

    if print_results:
        print(tt_result)
        print(df_var_long.groupby('origin')[var].describe())

    if plot_figure:
        if fig is None:
            fig = plt.figure()
        sns.swarmplot(data=df_var_long, x='origin', y=var, 
                    color='blue', edgecolor='gray', size=3)
        sns.lineplot(data=df_var_long, x='origin', y=var, hue='filename', 
                    marker=None, linewidth=0.2, 
                    palette=['k'] * df_var.shape[0],
                    legend=False, alpha=alpha)
        plt.tight_layout()
    else:
        fig = None
    return fig, tt_result


if __name__ == '__main__':
    basedir = './'
    imgdir = './images'
    if not os.path.exists(imgdir):
        os.mkdir(imgdir)

    df, df_wide = get_metrics_df(basedir)

    tt_results = {}
    # removed difficulty as it's fairly correlated with others
    plotvars = [ 'mi_mi', 'hal_bugs', 'hal_difficulty',
                'flake8_messages_per_loc', 
                'mean_cc', 'raw_comments', 'raw_lloc']

    for var in plotvars:
        fig, tt_results[var] = plot_var_swarm_plus_line(df, df_wide, var)
        fig.savefig(f'{imgdir}/{var}_swarmplot.png')


    # get fdr cutoff


    pvals = [tt_results[x].pvalue for x in plotvars]
    reject, pvals_corrected, alphacSidak, alphacBonf = multipletests(
        pvals,alpha=0.05, method='fdr_bh')
    fdr_pvals = pd.DataFrame({
        'var':plotvars, # 'pval':pvals, 
        'Median (github)': df.query('origin == "github"')[plotvars].mean(axis=0),
        'Median (GPT-4)': df.query('origin == "gpt4"')[plotvars].mean(axis=0),
        'Cohens d': None,
        'P-value (FDR)':pvals_corrected})
    
    for var in plotvars:
        diff = df.query('origin == "github"')[var].values - df.query('origin == "gpt4"')[var].values
        fdr_pvals.loc[var, 'Cohens d'] = np.abs(diff.mean() / diff.std())
    pd.set_option("display.precision", 3)
    print(fdr_pvals.drop('var', axis=1).round(decimals=3).to_markdown())
    # sns.heatmap(df_github[plotvars].corr(), annot=True, fmt='.2f', cmap='RdBu_r', center=0)
