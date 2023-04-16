# create a python wrapper for the statsmodels ttest_ind function, which takes the same arguments and returns a report similar to the one returned by the t.test function in R

import numpy as np
import scipy.stats as stats
from statsmodels.stats.weightstats import ttest_ind

def t_test_ind_report(a, b, alternative='two-sided', usevar='pooled', value=0, alpha=0.05):
    t_stat, p_value, df = ttest_ind(a, b, alternative=alternative, usevar=usevar, value=value)

    # Calculate the confidence interval
    pooled_std = np.sqrt(((len(a) - 1) * np.var(a, ddof=1) + (len(b) - 1) * np.var(b, ddof=1)) / (len(a) + len(b) - 2))
    margin_of_error = stats.t.ppf(1 - alpha / 2, df) * pooled_std * np.sqrt(1 / len(a) + 1 / len(b))
    mean_diff = np.mean(a) - np.mean(b)
    conf_int = (mean_diff - margin_of_error, mean_diff + margin_of_error)

    # Format the report
    report = (
        f"Two Sample t-test\n\n"
        f"t = {t_stat:.5f}, df = {df:.0f}, p-value = {p_value:.5f}\n"
        f"alternative hypothesis: true difference in means is not equal to {value}\n"
        f"95% confidence interval:\n"
        f" {conf_int[0]:.5f} {conf_int[1]:.5f}\n"
        f"sample estimates:\n"
        f"mean of x mean of y\n"
        f" {np.mean(a):.5f} {np.mean(b):.5f}"
    )
    return report


if __name__ == '__main__':
    # Example usage
    a = [24, 25, 26, 27, 28, 29, 30]
    b = [20, 21, 22, 23, 24, 25, 26]

    print(t_test_ind_report(a, b))
