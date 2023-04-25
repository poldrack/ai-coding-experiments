# run execution tests for conceptual prompting expt

import os
from pathlib import Path
import subprocess


def run_test(cmd, cwd=[]):
    """ run a command in the shell using Popen
    """
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, shell=True, check=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr



if __name__ == "__main__":
    dirs = sorted(Path('data/conceptual_prompting/testdirs').glob('concep*'))
    test_output = {}
    for d in dirs:
        # use Agg back end to prevent plotting of figures
        test_output[d] = run_test(f'MPLBACKEND=Agg python {d}/answer.py')
    
    nfailures = len([v for k, v in test_output.items() if 'Error' in v[1]])
    print(f'{nfailures} failures')
