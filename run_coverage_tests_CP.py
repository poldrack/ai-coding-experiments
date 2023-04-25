# run execution tests for conceptual prompting expt

import os
from pathlib import Path
import subprocess
import json
import pandas as pd


def run_cmd(cmd):
    """ run a command in the shell using Popen
    """
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, shell=True, check=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr


def extract_coverage(coverage):
    """ extract coverage from coverage report
    """
    coverage = coverage.split('\n')
    for line in coverage:
        if line.find('/answer.py') > -1:
            line = line.split()
            assert '%' in line[-1]
            return line[0], line[1], line[2], line[-1].replace('%', '')



if __name__ == "__main__":
    dirs = sorted(Path('data/conceptual_prompting/testdirs').glob('concep*'))
    coverage_file = Path('results/conceptual_prompting/code_coverage.json')
    if not os.path.exists(os.path.dirname(coverage_file)):
        os.makedirs(os.path.dirname(coverage_file))

    if not coverage_file.exists():
        coverage = {}
        for d in dirs:
            print(d.as_posix())
            result = run_cmd(f'coverage run -m pytest {d.as_posix()}')
            if len(result[1]) > 0:
                print(result[1])
            coverage[d.as_posix()] = run_cmd('coverage report')
        # save coverage
        with open(coverage_file, 'w') as f:
            json.dump(coverage, f)
    else:
        print('Using existing coverage file')
        with open(coverage_file, 'r') as f:
            coverage = json.load(f)

    all_coverage = []
    for k, v in coverage.items():
        all_coverage.append(extract_coverage(v[0]))
    
    coverage_df = pd.DataFrame(all_coverage, columns=['file', 'statements', 'missed', 'coverage'])
    coverage_df.to_csv('results/conceptual_prompting/code_coverage.csv', index=False)