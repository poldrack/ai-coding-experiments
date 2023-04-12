# select code from github for gpt-4 recoding

import os
import pandas as pd
import hashlib
import json

if __name__ == '__main__':
    # read in the csv file
    df = pd.read_csv('code_info_github.csv', index_col=0)
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
        hash = hashlib.sha256(filename.encode('utf-8')).hexdigest()
        header = f'please recode the following Python code.  Please return the code within an explicit code cell.\n'
        header += f'# {hash}\n'
        with open(filename) as f:
            code = header + f.read()
        codeinfo[hash] = {
            'filename': filename,
            'code': code,
        }
        with open(f'github_code_for_recoding/{hash}.txt', 'w') as f:
            f.write(code)
        
        with open('github_code_for_recoding_info.json', 'w') as f:
            json.dump(codeinfo, f)