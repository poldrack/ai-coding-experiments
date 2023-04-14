# select code from github for gpt-4 recoding

import os
import pandas as pd
import hashlib
import json
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', default='github')
    parser.add_argument('-o', '--outdir', default='github_code_for_recoding')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    print(args)

    infile = f'analysis_outputs/code_info_{args.dataset}.csv'
    # read in the csv file
    df = pd.read_csv(infile, index_col=0)
    df['github_license'] = df['github_license'].fillna('None')
    print(f'number of code files: {len(df)}')
    df = df.dropna()
    print(f'number of code files after dropna: {len(df)}')
    df = df.query('ntokens > 200 and ntokens < 1000')
    print(f'number of code files after ntoken filter: {len(df)}')

    codeinfo = {}

    for idx in df.index:
        filename = os.path.join('github_code',
                                df.loc[idx, 'filename'])
    
        hash = hashlib.sha256(filename.encode('utf-8')).hexdigest()[:20]
        assert hash not in codeinfo
    
        # prompt1: header = f'please recode the following Python code.  Please return the code within an explicit code cell.\n'
        header = "Please refactor the following Python code to be more readable, adding or rewriting comments as needed. Please embed the code within an explicit code block, surrounded by triple-backtick markers."
        header += f'# {hash}\n'
        with open(filename) as f:
            code = header + f.read()
        codeinfo[hash] = {
            'filename': filename,
            'code': code,
        }
        with open(f'{args.outdir}/{hash}.txt', 'w') as f:
            f.write(code)
        
        with open(f'{args.outdir}.json', 'w') as f:
            json.dump(codeinfo, f)