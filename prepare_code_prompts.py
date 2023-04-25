# this is for the conceptual prompting experiment

import os


with open('data/conceptual_prompting/coding_prompts.txt', 'r') as f:
    lines = [i.lstrip().strip() for i in f.readlines()]

with open('data/conceptual_prompting/coding_prompts_clean_v2.txt', 'w') as f:
    for i in lines:
        if i != '':
            f.write(i + 
    ' Please embed the code within an explicit code block, surrounded by triple-backtick markers. ' + 
    'Generate realistic values for any examples, and do not use input() commands. ' + 
    'Create code that is modular and well-commented.  Then, generate a set of pytest tests that exercise each of the functions, embedded in a separate code block.\n')