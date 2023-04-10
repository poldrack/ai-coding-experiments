# from codex paper: We filtered
# out files which were likely auto-generated, had average line
# length greater than 100, had maximum line length greater
# than 1000, or contained a small percentage of alphanumeric
# characters.

import pycld2 as cld2
import numpy as np
from guesslang import Guess
from pathlib import Path
import subprocess
import json


def get_linelengths(code):
    ll =  [len(line) for line in code]
    return np.mean(ll), np.max(ll)


def detect_nonenglish(code):
    _, _, _, detected_language = cld2.detect(' '.join(code),
                                        returnVectors=True)
    nonenglish = []
    for l in detected_language:
        if l[2] not in ['ENGLISH', 'Unknown']:
            nonenglish.append(l[2])
    
    return len(nonenglish) > 0, nonenglish


def guess_language(code):
    guess = Guess()
    return guess.language_name(' '.join(code))


def get_metrics(infile, metric):
    assert metric in ['cc', 'hal', 'raw', 'mi']
    try:
        output = subprocess.run(['radon', metric, '-j', infile], capture_output=True, text=True)
        result = json.loads(output.stdout)
        return result[infile.as_posix()]
    except:
        print(f'error running radon metric {metric} on ', infile)
        return None



infiles = Path('github_code').glob('**/*.py')

file_info = {}
for infile in infiles:
    with open(infile, 'r') as f:
        try:
            code= [i.strip() for i in f.readlines()]
        except UnicodeDecodeError:
            print('error reading', infile)
            file_info[infile] = None
            continue

    try:
        file_info[infile] = {'guess': guess_language(code),
                            'nonenglish': detect_nonenglish(code),
                            'mean_max_ll': get_linelengths(code)}
    except:
        print('error parsing', infile)
        file_info[infile] = None
    
    # Compute metrics
    for metric in ['cc', 'hal', 'raw', 'mi']:
        file_info[infile][metric] = get_metrics(infile, metric)
    

    print(file_info[infile])

with open('file_info.json', 'w') as f:
    json.dump(file_info, f)