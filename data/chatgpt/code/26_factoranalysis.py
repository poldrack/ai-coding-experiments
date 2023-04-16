# please create python code to 1) load data from https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/master/Data/Complete_02-16-2019/meaningful_variables.csv into a data frame, select all variables that begin with 'upps_impulsivity_survey', 'sensation_seeking_survey', 'bis11_survey', or 'dickman_survey', 3) perform exploratory factor analysis over these variables using a range of 1 to 5 factors, 4) identify which model is preferred based on minimum BIC, and 5) for each factor in the preferred solution, display which variables were more strongly loaded on that factor versus other factors.  Please write this in a modular way and output one function at a time.
# FactorAnalyzer does not have a "bic" variable or method so the code crashes
# I do not want to use explained variance ratio because it does not penalize for model complexity.  please use a different model selection criterion that penalizes for complexity.
# -- tries to use KMO which is not a model selection criterion
# KMO is not a model selection criterion.  perhaps you can use a different package to perform factor analysis that can provide BIC directly?
# - tries to use fa from R via rpy2
# the fa package does not seem to be available.  please use the psych package instead to perform factor analysis
# failes with rpy2 error, gave up

import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr

# Activate pandas conversion for rpy2
pandas2ri.activate()

# Load R libraries
base = importr('base')
stats = importr('stats')
psych = importr('psych')


def load_data(url: str) -> pd.DataFrame:
    data = pd.read_csv(url)
    return data


def select_variables(data: pd.DataFrame, prefixes: list) -> pd.DataFrame:
    selected_vars = data.columns[data.columns.str.startswith(tuple(prefixes))]
    return data[selected_vars]


def perform_efa(data: pd.DataFrame, min_factors: int, max_factors: int) -> dict:
    r_data = pandas2ri.py2rpy(data)
    efa_results = {}
    for n_factors in range(min_factors, max_factors + 1):
        efa = psych.fa(r_data, nfactors=n_factors, fm="minres", n_obs=data.shape[0])
        efa_results[n_factors] = efa
    return efa_results


def find_preferred_model(efa_results: dict) -> int:
    bic_values = {n_factors: efa.rx2('BIC')[0] for n_factors, efa in efa_results.items()}
    preferred_n_factors = min(bic_values, key=bic_values.get)
    return preferred_n_factors


def display_strongly_loaded_variables(efa_results: dict, preferred_n_factors: int, data: pd.DataFrame) -> None:
    efa = efa_results[preferred_n_factors]
    loadings = pandas2ri.rpy2py(efa.rx2('loadings'))

    for i in range(preferred_n_factors):
        print(f"Factor {i + 1}:")
        strongly_loaded_vars = loadings[loadings.iloc[:, i] == loadings.max(axis=1)].iloc[:, i]
        print(strongly_loaded_vars.sort_values(ascending=False))
        print("\n")


if __name__ == "__main__":
    data_url = "https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/master/Data/Complete_02-16-2019/meaningful_variables.csv"
    prefixes = ['upps_impulsivity_survey', 'sensation_seeking_survey', 'bis11_survey', 'dickman_survey']

    data = load_data(data_url)
    selected_data = select_variables(data, prefixes)
    efa_results = perform_efa(selected_data, min_factors=1, max_factors=5)
    preferred_n_factors = find_preferred_model(efa_results)
    display_strongly_loaded_variables(efa_results, preferred_n_factors, selected_data)
