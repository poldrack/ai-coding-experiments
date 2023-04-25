# %%
import json
import collections
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path


# %%
flake8_error_messages = {
    "E101": "Indentation contains mixed spaces and tabs",
    "E111": "Indentation is not a multiple of four",
    "E112": "Expected an indented block",
    "E113": "Unexpected indentation",
    "E114": "Indentation is not a multiple of four (comment)",
    "E115": "Expected an indented block (comment)",
    "E116": "Unexpected indentation (comment)",
    "E117": "Over-indented",
    "E121": "Continuation line under-indented for hanging indent",
    "E122": "Continuation line missing indentation or outdented",
    "E123": "Closing bracket does not match indentation of opening bracket's line",
    "E124": "Closing bracket does not match visual indentation",
    "E125": "Indentation does not match any outer indentation level",
    "E126": "Continuation line over-indented for hanging indent",
    "E127": "Continuation line over-indented for visual indent",
    "E128": "Continuation line under-indented for visual indent",
    "E129": "Visually indented line with same indent as next logical line",
    "E131": "Continuation line unaligned for hanging indent",
    "E133": "Closing bracket is missing indentation",
    "E201": "Whitespace after '('",
    "E202": "Whitespace before ')'",
    "E203": "Whitespace before ':'",
    "E211": "Whitespace before '('",
    "E221": "Multiple spaces before operator",
    "E222": "Multiple spaces after operator",
    "E223": "Tab before operator",
    "E224": "Tab after operator",
    "E225": "Missing whitespace around operator",
    "E226": "Missing whitespace around arithmetic operator",
    "E227": "Missing whitespace around bitwise or shift operator",
    "E228": "Missing whitespace around modulo operator",
    "E231": "Missing whitespace after ',', ';', or ':'",
    "E241": "Multiple spaces after ','",
    "E242": "Tab after ','",
    "E251": "Unexpected spaces around keyword / parameter equals",
    "E252": "Missing whitespace around parameter equals",
    "E261": "At least two spaces before inline comment",
    "E262": "Inline comment should start with '# '",
    "E265": "Block comment should start with '# '",
    "E271": "Multiple spaces after keyword",
    "E272": "Multiple spaces before keyword",
    "E275": "Missing whitespace after keyword",
    "E266": "Too many leading '#' for block comment",
    "E301": "Expected 1 blank line, found 0",
    "E302": "Expected 2 blank lines, found 0",
    "E303": "Too many blank lines (3)",
    "E304": "Blank lines found after function decorator",
    "E305": "Expected 2 blank lines after class or function definition, found 1",
    "E306": "Expected 1 blank line before a nested definition",
    "E401": "Multiple imports on one line",
    "E402": "Module level import not at top of file",
    "E501": "Line too long (82 > 79 characters)",
    "E502": "The backslash is redundant between brackets",
    "E701": "Multiple statements on one line (colon)",
    "E702": "Multiple statements on one line (semicolon)",
    "E703": "Statement ends with a semicolon",
    "E704": "Multiple statements on one line (def)",
    "E711": "Comparison to None should be 'if cond is None:'",
    "E712": "Comparison to True should be 'if cond is True:' or 'if cond:'",
    "E713": "Test for membership should be 'not in'",
    "E714": "Test for object identity should be 'is not'",
    "E721": "Do not compare types, use 'isinstance()'",
    "E722": "Do not use bare 'except'",
    "E731": "Do not assign a lambda expression, use a def",
    "E741": "Ambiguous variable name 'l'",
    "E742": "Ambiguous function definition name 'l'",
    "E743": "Ambiguous class definition name 'l'",
    "E901": "SyntaxError or IndentationError",
    "E902": "TokenError: EOF in multi-line statement",
    "E999": "SyntaxError: failed to compile",
    "F401": "Module imported but unused",
    "F402": "Import module from line N shadowed by loop variable",
    "F403": "'from module import *' used; unable to detect undefined names",
    "F404": "Future import(s) name after other statements",
    "F405": "Name may be undefined, or defined from star imports: module",
    "F406": "'from module import *' only allowed at the module level",
    "F407": "An undefined __future__ feature name was imported",
    "F541": "f-string is missing placeholders",
    "F601": "Dictionary key name repeated with different values",
    "F602": "Dictionary key variable name shadowing an outer scope variable",
    "F621": "Too many expressions in an assignment with star-unpacking",
    "F622": "Two or more starred expressions in an assignment (a, *b, *c = d)",
    "F631": "assertion test is a tuple, which are always True",
    "F632": "use ==/!= to compare str, bytes, and int literals",
    "F633": "don't use `l`, `O`, or `I` as variable names",
    "F701": "A break statement outside of a while or for loop",
    "F702": "A continue statement outside of a while or for loop",
    "F703": "A continue statement in a finally block in a loop",
    "F704": "A yield or yield from statement outside of a function",
    "F705": "A return statement with arguments inside a generator",
    "F706": "A return statement outside of a function/method",
    "F707": "An except: block as not the last exception handler",
    "F811": "Redefinition of unused name from line N",
    "F812": "List comprehension redefines name from line N",
    "F821": "Undefined name 'name'",
    "F822": "Undefined name 'name' in __all__",
    "F823": "Local variable 'name' defined in enclosing scope on line N referenced before assignment",
    "F841": "Local variable 'name' is assigned to but never used",
    "F901": "SyntaxError: invalid syntax",
    "W191": "Indentation contains tabs",
    "W291": "Trailing whitespace",
    "W292": "No newline at end of file",
    "W293": "Blank line contains whitespace",
    "W391": "Blank line at end of file",
    "W503": "Line break occurred before a binary operator",
    "W504": "Line break occurred after a binary operator",
    "W601": ".has_key() is deprecated, use 'in'",
    "W602": "Deprecated form of raising exception",
    "W603": "'<>' is deprecated, use '!='",
    "W604": "Backticks are deprecated, use 'repr()'",
    "W605": "Invalid escape sequence 'x'",
    "W606": "'async' and 'await' are reserved keywords starting with Python 3.7",
}


# %%
def process_flake8_errors(flake8_errors):
    """
    Process flake8 errors to remove the line number and the error code
    """
    processed_errors = []
    for error in flake8_errors:
        if len(error) == 0:
            continue
        error = ' '.join(error.split('.py')[1].split(' ')[1:])
        processed_errors.append(error)
    return processed_errors


def get_error_df(basedir):
    if isinstance(basedir, str):
        basedir = Path(basedir)
    

    with open(basedir / 'results/github/code_analytics.json', 'r') as f:
        github_data = json.load(f)

    with open(basedir / 'results/gpt4/code_analytics.json', 'r') as f:
        gpt4_data = json.load(f)

    shared_keys = set(github_data.keys()).intersection(
        gpt4_data.keys())

    github_data = {k: github_data[k] for k in shared_keys}
    gpt4_data = {k: gpt4_data[k] for k in shared_keys}

    flake8_errors = {'github': [], 'gpt4': []}
    errorcounts = {'github': None, 'gpt4': None}
    error_df = {'github': None, 'gpt4': None}
    for dataset, data in zip(['github', 'gpt4'], [github_data, gpt4_data]):
        
        for filename, info in data.items():
            if info is not None and 'flake8' in info:
                errors = process_flake8_errors(info['flake8'])
                flake8_errors[dataset].extend(
                    [i.split(' ')[0] for i in errors if len(i) > 0])


        errorcounts[dataset] = collections.Counter(
            flake8_errors[dataset])
        error_df[dataset] = pd.DataFrame(
            errorcounts[dataset].items(), 
            columns=['errorcode', 'count'])
        error_df[dataset]['dataset'] = dataset
    return error_df

def get_joined_errors(error_df):

    all_errors = pd.concat([error_df['github'], error_df['gpt4']])

    # %%
    errors_joined = error_df['github'].merge(
        error_df['gpt4'], on='errorcode', how='outer')

    # %%
    errors_joined['sum_errors'] = errors_joined['count_x'] +\
        errors_joined['count_y']
    sum_threshold = 50
    errors_joined = errors_joined[errors_joined['sum_errors'] > sum_threshold]
    errors_joined = errors_joined.sort_values(by='count_x',
                                            ascending=False)

    all_errors = all_errors[all_errors['errorcode'].isin(
        errors_joined['errorcode'])]


    all_errors.sort_values(by='count', 
                        ascending=True,
                        inplace=True)
    return all_errors, errors_joined

def plot_errors(error_df, figsize=None,
                font_scale=1.5, label_length=40):
    if figsize is None:
        figsize = (10, 8)

    all_errors, errors_joined = get_joined_errors(error_df)

    fig = plt.figure(figsize=figsize)
    sns.set(font_scale=font_scale)
    labels = [flake8_error_messages[i][:label_length] for i in errors_joined['errorcode']]
    bp = sns.barplot(y='errorcode', x='count', 
                hue='dataset', data=all_errors,
                orient='h', order=errors_joined['errorcode'],
                hue_order = ['github', 'gpt4'])
    bp.set_yticks(range(len(labels)), labels=labels)
    ax = plt.gca()
    ax.invert_xaxis()
    plt.tick_params(axis = 'y', left = False, 
                    right = True, labelleft = False, 
                    labelright = True)
    plt.ylabel('Warning/error codes')
    plt.tight_layout()
    return fig

if __name__ == "__main__":

    basedir = Path('/home/poldrack/Dropbox/code/talks-AIAssistedCoding')
    error_df = get_error_df(basedir)
    fig = plot_errors(error_df)
    fig.savefig('/home/poldrack/Dropbox/Documents/Presentations/talks-AIAssistedCoding/talk/images/flake8_errors.png', dpi=300, bbox_inches='tight')

