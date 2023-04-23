# run pytest tests for conceptual prompting expt

import os
from pathlib import Path
import subprocess
import pandas as pd
import re




def run_test(cmd, cwd=[]):
    """ run a command in the shell using Popen
    """
    stdout_holder=[]
    if cwd:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,cwd=cwd)
    else:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout:
        stdout_holder.append(line.strip())
    process.wait()
    return [i.decode('utf-8') for i in stdout_holder]


def extract_test_results(line):
    """
    Extract the number of passed and failed tests from a pytest output line.

    :param line: A string representing a pytest output line.
    :return: A tuple with the number of failed and passed tests.
    """
    assert 'failed' in line or 'passed' in line or 'error' in line
    # Define regex patterns for failed and passed tests
    failed_pattern = r"(\d+) failed"
    passed_pattern = r"(\d+) passed"
    error_pattern = r"(\d+) error"

    # Search for the patterns in the line
    failed_match = re.search(failed_pattern, line)
    passed_match = re.search(passed_pattern, line)
    error_match = re.search(error_pattern, line)

    # Extract the numbers and convert to integers
    failed_tests = int(failed_match.group(1)) if failed_match else 0
    passed_tests = int(passed_match.group(1)) if passed_match else 0
    error_tests = int(error_match.group(1)) if error_match else 0

    return (failed_tests, passed_tests, error_tests)


def get_errors(test_output):
    n_errors = 0
    n_failed = 0
    if 'error' in test_output[-1]:
        n_errors = int(test_output[-1].split(' ')[1])
    if 'failed' in test_output[-1]:
        n_failed = int(test_output[-1].split(' ')[1])
    errors = []
    for line in test_output:
        if 'Did you mean' in line:
            continue
        if 'E   ' in line:
            if 'assert' in line or 'Error' in line:
                errors.append(line)
    try:
        assert len(errors) == (n_errors + n_failed)
    except AssertionError:
        print('AssertionError')
        print(test_output)
        print(f'len(errors) = {len(errors)}')
        print(f'n_errors + n_failed = {n_errors + n_failed}')
        raise AssertionError
    return n_errors, n_failed, errors

if __name__ == "__main__":
    coverage_df = pd.read_csv('results/conceptual_prompting/code_coverage.csv')
    coverage_df['test_success'] = False
    coverage_df['ntests'] = None
    success = {}
    failure = {}
    for idx in coverage_df.index:
        d = os.path.dirname(coverage_df.loc[idx, 'file'])
        # use Agg backend to avoid opening a window
        test_output = run_test(f'MPLBACKEND=Agg python -m pytest {d}')
        coverage_df.loc[idx, 'ntests'] = int(test_output[4].split(' ')[1])
        if 'passed' in test_output[-1] and 'failed' not in test_output[-1]:
            success[d] = test_output[-1]
            coverage_df.loc[idx, 'test_success'] = True
        else:
            print(d)
            failure[d] = test_output
            n_errors, n_failed, errors = get_errors(test_output)
            print(get_errors(test_output))
            print('')


    coverage_df.to_csv('results/conceptual_prompting/code_coverage.csv', index=False)