# Combine info from file_info.json and codeinfo.json into a single data frame

import json
import pandas as pd
import argparse


def meets_requirements(dct, key, max_mean_line_length=100, 
                       max_max_line_length=1000, max_tokens=2500,
                       verbose=False):
    """
    from codex paper: We filtered out files which were likely auto-generated, had average line
    length greater than 100, had maximum line length greater
    than 1000, or contained a small percentage of alphanumeric
    characters.
    """
    # is it a Python file?
    if dct['guess'] != 'Python':
        if verbose:
            print(f'Not a Python file: {key}')
        return False
    
    # does it include non-English text?
    if dct['nonenglish'][0]:
        if verbose:
            print(f'Non-English text: {key}')
        return False
    
    # is it auto-generated?
    if dct['autogen']:
        if verbose:
            print(f'Auto-generated: {key}')
        return False
    
    # is it obfuscated?
    if dct['obfuscations'] > 1000:
        if verbose:
            print(f'Obfuscated: {key}')
        return False
    
    # is file size too large?
    if dct['filesize'] > 1000000:
        if verbose:
            print(f'File size too large: {key}')
        return False
    
    # do mean and max line lengths fit within limits?
    if dct['mean_max_ll'][0] > max_mean_line_length or dct['mean_max_ll'][1] > max_max_line_length:
        if verbose:
            print(f'Mean or max line length too large: {key}')
        return False
    
    if dct['ntokens'] > max_tokens:
        if verbose:
            print(f'Number of tokens too large: {key}')
        return False

    return True


def add_mean_complexity(file_info):
    for k, v in file_info.items():
        if v is None or 'cc' not in v or v['cc'] is None or len(v['cc']) == 0:
            continue

        file_info[k]['mean_cc'] = 0
        for i in v['cc']:
            if 'complexity' not in i:
                continue
            file_info[k]['mean_cc'] += i['complexity']
        file_info[k]['mean_cc'] = file_info[k]['mean_cc'] / len(v['cc'])
    return(file_info)


def fix_hal_metrics(file_info):
    # move total metrics into main hal dict
    for k, v in file_info.items():
        if v is None or 'hal' not in v or v['hal'] is None:
            continue

        if 'total' in v['hal']:
            for metric, value in v['hal']['total'].items():
                v['hal'][metric] = value
            del v['hal']['total']
    return(file_info)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', default='github', 
                        help='dataset label')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='verbose output')
    parser.add_argument('--no-filter', action='store_true', 
                        help='do not filter out files that do not meet requirements')
    parser.add_argument('--secondary-key',
                        help='secondary key to use for file info (e.g., "gpt4")')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    print(args)
    
    vars_to_save = {
        'raw': ['loc', 'lloc', 'comments'],
        'mi': ['mi'],
        'hal': ['bugs', 'difficulty', 'volume'],
        'github': ['commit', 'license']
    }

    # Read in the file info
    with open(f'analysis_outputs/file_info_{args.dataset}.json') as f:
        file_info = json.load(f)

    original_length = len(file_info)

    # filter out the files that don't meet requirements
    orig_keys = list(file_info.keys())
    if not args.no_filter:
        for k in orig_keys:
            if file_info[k] is None or not meets_requirements(
                    file_info[k], k, verbose=args.verbose):
                del file_info[k]

        print(f'Filtered out {original_length - len(file_info)} files that did not meet requirements.')
    print(f'Found {len(file_info)} files.')

    if args.secondary_key is not None:
        print(f'Filtering out files that are not in {args.secondary_key}...')
        with open(f'analysis_outputs/file_info_{args.secondary_key}.json') as f:
            file_info2 = json.load(f)
        selected_file_info = {}
        for k in file_info2.keys():
            if k in file_info:
                selected_file_info[k] = file_info[k]
        file_info = selected_file_info

        print(f'Filtered out {original_length - len(file_info)} files that did not meet requirements.')
        print(f'Kept {len(file_info)} files.')
        
    # Read in the code info
    with open('codeinfo.json') as f:
        code_info = json.load(f)

    file_info = add_mean_complexity(file_info)

    # Create a data frame from the file info
    df = pd.DataFrame.from_dict(
        {'filename': list(file_info.keys())})

    for vars in ['mean_cc', 'ntokens', 'flake8_nsyntaxerrors',
                 'flake8_nmessages', 'filesize', 'obfuscations',
                 'autogen', 'nfuncs']:
        for i in df.index:
            f = df.loc[i, 'filename']
            if file_info[f] is not None and vars in file_info[f]:
                df.loc[i, vars] = file_info[f][vars]
            else:
                df.loc[i, vars] = None
    
    file_info = fix_hal_metrics(file_info)

    for var, subvar in vars_to_save.items():
        for s in subvar:
            results = []
            for i in df.filename:
                if file_info[i] is None or var not in file_info[i]:
                    results.append(None)
                elif file_info[i][var] is None:
                    results.append(None)
                elif s not in file_info[i][var]:
                    results.append(None)
                else:
                    results.append(file_info[i][var][s])
            df[f'{var}_{s}'] = results


    # Save the data frame
    if args.secondary_key is not None:
        sec_key = f'_filt-{args.secondary_key}'
    else:
        sec_key = ''
    if args.no_filter:
        filter_key == ''
    else:
        filter_key = '_filtered'
    df.to_csv(f'analysis_outputs/code_info_{args.dataset}{sec_key}{filter_key}.csv')
