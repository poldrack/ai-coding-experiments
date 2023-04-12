## Code analysis


### Step 1: download code from github

- `download_github_code.py` uses the github api to download code files labeled as Python files.  The code used an invalid search term (dates are not actually accepted for github API calls) so the code was not date-limited.  Because the github search API is heavily rate-limited, the throughput is on the order of two files per minute.

For each file, the API is also used to load the commit history (to obtain the date of the commit) and the license information for the repository.

After running for a number of hours, a total of 2129 code files were downloaded.


### Step 2: process and filter code

- `process_github_code.py` performs a set of analyses on each code file from a given source ('github' or 'chatgpt'):
  - It runs the `flake8` linter and stores all messages.
  - It performs code quality analyses using the `radon` package, including cylcomatic complexity, Halstead metrics, and maintainability metric, along with raw metrics such as lines of code and comments and number of defined functions
  - It computes a number of metrics used for later filtering (based on the filtering approach used in the Codex paper), including:
    -  mean and maximum line length
    -  a guess of the programming language
    -  the presence of non-English language in the code
    -  the presence of potential markers of automatic generation
    -  the presence of potential obfuscation (the "if x - y:" pattern)

Results from this step are saved to `file_info_<source>.json`.


### Step 3: summarize code metrics

- `summarize_code_info.py` summarizes the results from step 2 into a tabular data frame for further analysis.

Files are filtered out based on the following requirements:

- Must be identified as a Python file by `guesslang`
- Must not include text identified as non-English by `pycld2.detect`
- Must not include strings that suggest potential autogeneration
- Must not include evidence of "if x - y:" obfuscation
- Must not be over 1 MB in size
- Must have mean line length < 100 and maximum line length < 1000
- Must contain fewer than 2500 tokens using the `cl100k_base` encoding from `tiktoken`

### Step 4: Select code for analysis

`select_code_for_recoding.py`

### Step 4: analysis of code metrics

`CodeAnalysis.py` is a notebook file (using jupytext py:percent mode) to analyze the results.