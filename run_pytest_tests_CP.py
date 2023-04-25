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

    return (passed_tests, failed_tests, error_tests)


def get_errors(test_output):
    npassed, nfailed, nerrors = extract_test_results(test_output[-1])

    messages = []
    if nfailed > 0:
        for i, line in enumerate(test_output):
            if len(line) == 0:
                continue
            if line[0] == '>' and len(test_output[i + 1]) > 0 and test_output[i+1][0] == 'E':
                messages.append(line + test_output[i+1])
    if nerrors > 0:
        for i, line in enumerate(test_output):
            if len(line) == 0:
                continue
            if line[0] == 'E' and 'Error' in line:
                messages.append(line)
    try:
        assert len(messages) == (nerrors + nfailed)
    except AssertionError:
        print('AssertionError')
        print(test_output)
        print(f'len(errors) = {len(messages)}')
        print(f'n_errors + n_failed = {nerrors + nfailed}')
        raise AssertionError
    return messages

if __name__ == "__main__":
    coverage_df = pd.read_csv('results/conceptual_prompting/code_coverage.csv')
    coverage_df['test_success'] = False
    coverage_df['ntests'] = None
    error_types = ['assert_errors', 'raise_errors',
                    'other_errors', 'type_errors',
                    'value_errors', 'index_errors',
                    'zerodiv_errors']
    for e in error_types:
        coverage_df[e] = 0
    success = {}
    failure = {}
    for idx in coverage_df.index:
        d = os.path.dirname(coverage_df.loc[idx, 'file'])
        # use Agg backend to avoid opening a window
        test_output = run_test(f'MPLBACKEND=Agg python -m pytest {d}')
        coverage_df.loc[idx, 'ntests'] = int(test_output[4].split(' ')[1])
        npassed, nfailed, nerrors = extract_test_results(test_output[-1])

        print(coverage_df.loc[idx, 'ntests'], npassed, nfailed, nerrors)

        coverage_df.loc[idx, ['npassed', 'nfailed', 'nerrors']] = [
            npassed, nfailed, nerrors]
        if nfailed == 0 and nerrors == 0:
            success[d] = test_output[-1]
            coverage_df.loc[idx, 'test_success'] = True
        else:
            print(d)
            failure[d] = test_output
            errors = get_errors(test_output)
            print(get_errors(test_output))
            print('')
            coverage_df.loc[idx, 'messages'] = ';'.join(errors)
            for e in errors:
                print(e)
                if 'ZeroDivisionError' in e:
                    coverage_df.loc[idx,'zerodiv_errors'] += 1
                elif re.search(r'>\s*assert', e):
                    coverage_df.loc[idx, 'assert_errors'] += 1
                elif re.search(r'>\s*np.testing.assert', e):
                    coverage_df.loc[idx, 'assert_errors'] += 1
                elif re.search(r'>\s*with pytest.raises', e):
                    coverage_df.loc[idx,'raise_errors'] += 1
                elif re.search(r'E\s*TypeError', e):
                    coverage_df.loc[idx,'type_errors'] += 1
                elif re.search(r'E\s*IndexError', e):
                    coverage_df.loc[idx,'index_errors'] += 1
                elif re.search(r'E\s*ValueError', e):
                    coverage_df.loc[idx,'value_errors'] += 1
                else:
                    coverage_df.loc[idx,'other_errors'] += 1

    coverage_df.to_csv('results/conceptual_prompting/code_coverage.csv', index=False)

    for et in error_types:
        print(f'n {et}:', coverage_df.query(f'{et} > 0').shape[0])
