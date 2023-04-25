import json
from pathlib import Path
import os

def extract_python_cells(text):
    # this is version for conceptual prompting where
    # all outputs have two code blocks - first is code, second is test

    if isinstance(text, list):
        lines = text
    elif isinstance(text, str):
        lines = text.split('\n')
    else:
        raise ValueError('text must be list or str')

    ticklines = []
    for i, line in enumerate(lines):
        # find ticks
        if '```' in line:
            ticklines.append(i)

    return '\n'.join(lines[ticklines[0]+1:ticklines[1]]), '\n'.join(lines[ticklines[2]+1:ticklines[3]])

def check_backticks(code):
    codelines = code.split('\n')
    bt_counter = 0
    for l in codelines:
        if '```' in l:
            bt_counter += 1
    return bt_counter


def save_rawfiles(data: dict, outdir: Path):
    rawdir = outdir / 'raw'
    rawdir.mkdir(parents=True, exist_ok=True)

    for i, d in enumerate(data):
        answer = d['answer']
        if check_backticks(answer) != 4:
            print('Error in answer', i, check_backticks(answer))
        with open(rawdir / f'conceptual_prompting{i:02}.txt', 'w') as f:
            f.write(answer)


def fix_test_imports(test: str):
    """
    we don't know the name of the module being tested
    so we need to replace the import with the correct name
    """
    test = test.split('\n')
    inserted = False
    for i, c in enumerate(test):
        if 'import' in c:
            try:
                exec(c)
            # heuristic to guess the line of the import - seems to work
            except ModuleNotFoundError:
                # use a wildcard import here because we don't know the name of the functions
                test[i] = 'from answer import *'
                inserted = True
            except Exception as e:
                print('Error in test', i, e)
    if not inserted:
        test.insert(0, 'from answer import *')
    return '\n'.join(test)


if __name__ == '__main__':
    with open('data/conceptual_prompting/outputs_of_ConceptualPromptingV2Split.json') as f:
        data = json.load(f)


    outdir = Path('results/conceptual_prompting')

    # this is turned off because the raw files are already saved
    # several had to be manually edited to fix backtick issues
    save_raw = False
    if save_raw:
        save_rawfiles(data, outdir)


    rawdir = outdir / 'raw'
    rawfiles = sorted(rawdir.glob('*.txt'))

    code = {}
    test = {}
    for i, f in enumerate(rawfiles):
        with open(f) as f:
            raw = f.readlines()
        code[i], test[i] = extract_python_cells(raw)

    # save code to data dir for checking
    codedir = 'data/conceptual_prompting/code'
    os.makedirs(codedir, exist_ok=True)
    for i, c in code.items():
        with open(os.path.join(codedir, f'conceptual_prompting{i:02}.py'), 'w') as f:
            f.write(c)
    
    # save code/test pairs to separate dirs for testing
    testdir = 'data/conceptual_prompting/testdirs'
    os.makedirs(testdir, exist_ok=True)
    for i, (c, t) in enumerate(zip(code.values(), test.values())):
        os.makedirs(os.path.join(testdir, f'conceptual_prompting{i:02}'), exist_ok=True)
        t = fix_test_imports(t)
        with open(os.path.join(testdir, f'conceptual_prompting{i:02}', 'answer.py'), 'w') as f:
            f.write(c)
        with open(os.path.join(testdir, f'conceptual_prompting{i:02}', 'test_answer.py'), 'w') as f:
            f.write(t)
    
    