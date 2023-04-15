# this is for the conceptual prompting experiment

import os


with open('data/coding_prompts.txt', 'r') as f:
    lines = [i.lstrip().strip() for i in f.readlines()]

with open('data/coding_prompts_clean.txt', 'w') as f:
    for i in lines:
        if i != '':
            f.write(i + ' Please embed the code within an explicit code block, surrounded by triple-backtick markers.\n')