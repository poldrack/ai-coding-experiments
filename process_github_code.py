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
import tiktoken
import argparse


tokenizer = tiktoken.get_encoding("cl100k_base")

# Get the number of tokens for a string, measured using tiktoken
def getTokenLength(code):
    tokens = tokenizer.encode(' '.join(code))
    return len(tokens)


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
        print(result)
        return result[infile.as_posix()]
    except:
        print(f'error running radon metric {metric} on ', infile)
        return None


def get_file_info(infile, code):
    try:
        return {'guess': guess_language(code),
                            'nonenglish': detect_nonenglish(code),
                            'mean_max_ll': get_linelengths(code)}
    except:
        return None


# from https://stackoverflow.com/questions/50916422/python-typeerror-object-of-type-int64-is-not-json-serializable
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', default='github', help='dataset label')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    codedir = Path(f'{args.dataset}_code')
    assert codedir.exists(), f'code directory {codedir} does not exist'
    infiles = codedir.glob('**/*.py')
    maxfiles = 1000000
    
    file_info = {}
    for infile in infiles:
        fname = infile.as_posix()
        with open(infile, 'r') as f:
            try:
                code= [i.strip() for i in f.readlines()]
            except UnicodeDecodeError:
                print('error reading', infile)
                file_info[fname] = None
                continue


        file_info[fname] = get_file_info(infile, code)
        if file_info[fname] is None:
            print('error parsing', fname)
            continue

        file_info[fname]['ntokens'] = getTokenLength(code)

        # Compute metrics
        for metric in ['cc', 'hal', 'raw', 'mi']:
            file_info[fname][metric] = get_metrics(infile, metric)
        print(fname, file_info[fname])
        if len(file_info) > maxfiles:
            break

    with open(f'file_info_{args.dataset}.json', 'w') as f:
        json.dump(file_info, f, cls=NpEncoder)