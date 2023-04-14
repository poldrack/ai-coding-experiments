import json
from extract_text import extract_python_code, extract_text_from_comments_and_strings
import re
import os


def extract_python_code(text, key):
    # need to deal with the case where 
    # the code is not in a code block

    lines = text.split('\n')
    has_tripple_backtick = "```" in ' '.join(lines)
    python_code = []
    record = not has_tripple_backtick
    for line in lines:
        # check for key
        if bool(re.match(f'^# {key}', line)):
            continue
        if bool(re.match('^(Here|The|This) \w+', line)):
            continue
        if line.startswith('I am sorry'):
            print('Skipping because of recoding failure')
            return None
        if line.startswith('```'):
            record = True
            continue
        # deal with various unmarked endings
        if record and (line.startswith('```') or
            bool(re.match("^(I|The|In|Remember|I've|Make|Please|Simply|Above|You|Some|If|To|Let|Here's|Copy|Note:|Note|Use) (\w+|`)", line))) or\
            bool(re.match('^- \w+', line)):
            print("found stop line:", line)
            break
        if record:
            python_code.append(line)
    return python_code

if __name__ == "__main__":
    with open('gpt4_recoded_output.json', 'r') as f:
        gpt4_recoded_output = json.load(f)
    print(f'Loaded {len(gpt4_recoded_output)} recoded files')

    with open('github_code_for_recoding_info.json', 'r') as f:
        github_info = json.load(f)

    outdir = 'github_code_recoded_gpt4'
    os.makedirs(outdir, exist_ok=True)

    raw_outdir = 'github_code_recoded_gpt4_raw_output'
    os.makedirs(raw_outdir, exist_ok=True)
   

    items = {}
    for item in gpt4_recoded_output:
        key = item['key']
        print(key)
        items[key] = item
        raw_filename = github_info[key]['filename'].replace(
            'github_code', raw_outdir)
        assert raw_filename != github_info[key]['filename']
        with open(raw_filename, 'w') as f:
            f.write(item['answer'])
        items[key]['code'] = extract_python_code(item['answer'], key)
        #text = extract_text_from_comments_and_strings(item['code'])
        filename = github_info[key]['filename'].replace(
            'github_code', 'github_code_recoded_gpt4')
        assert filename != github_info[key]['filename']
        with open(filename, 'w') as f:
            f.write('\n'.join(item['code']))
        
