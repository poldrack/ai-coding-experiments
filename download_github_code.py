# RP: Create python code that uses the github api to download the 100 most recently committed python files.
# GPT4: To download the 100 most recently committed Python files using the GitHub API, you can use the requests library in Python. Make sure you have it installed by running pip install requests. You will also need a GitHub personal access token, which you can create by following these steps: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
# Replace your_github_token with your personal access token in the code below:
# followed up with: please only download one file from each user, so that the 100 files come from 100 unique users.
# followed up with:please make two changes.  first, read in the github token from a text file called "github_token.txt".  Second, create a variable called sleeptime that is set to 10 seconds. then place a time.sleep command after each call to the github api
# followed up with: please add a call to time.sleep after the download_file call in the main block
# followed with: if python_files exists, please delete all existing python files before running.

# this version has additional manual edits by RP


import requests
import os
import time
import json
from datetime import datetime, timedelta


def get_datelist():
    # end on date of GPT-4 release
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 3, 14)
    date_list = []

    while start_date <= end_date:
        date_string = start_date.strftime('%Y-%m-%d')
        date_list.append(date_string)
        start_date += timedelta(days=1)
    return date_list


def sleep(sleeptime=30):
    print(f"Sleeping for {sleeptime} seconds")
    time.sleep(sleeptime)


def download_file(file_url, file_path, verbose=True):
    response = requests.get(file_url, headers=headers)
    if verbose:
        print(f"Downloading {file_path}")
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return response.content


def get_recent_python_files(page_number, date=None):
    if date is None:
        datestr = ''
    else:
        datestr = f"+pushed:>{date}"
    search_url = f"https://api.github.com/search/code?q=language:python+extension:py+in:path{datestr}&sort=pushed&order=desc&per_page=100&page={page_number}"
    print(search_url)
    response = requests.get(search_url, headers=headers)
    return response.json()


def get_license(item):
    owner = item['repository']['owner']['login']
    repo = item['repository']['name']
    license_url = f"https://api.github.com/repos/{owner}/{repo}/license"
    license_result = requests.get(license_url, headers=headers)
    license_info = license_result.json()
    return license_info["license"]['name'] if "license" in license_info else None


def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")


def get_commit_date(item):
    owner = item['repository']['owner']['login']
    repo = item['repository']['name']
    commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits?path={item['path']}"
    commit_result = requests.get(commit_url, headers=headers)
    sleep(10)
    commit_info = commit_result.json()
    if len(commit_info) == 0:
        return None
    return commit_info[0]['commit']['author']['date']


def codesearch(dates, codeinfo, unique_users):
    for date in dates:
        print(f"Searching for files created on {date}...")
        for page_number in range(1, 9):
            good_search = False
            while not good_search:
                recent_python_files = get_recent_python_files(page_number, date)
                if 'message' in recent_python_files:
                    print(recent_python_files['message'])
                    sleep(300)
                else:
                    good_search = True
                    sleep()
            if 'message' in recent_python_files:
                print(recent_python_files['message'])
                break
            for item in recent_python_files["items"]:
                if item['repository']['owner']['login'] not in unique_users:
                    tag = item['repository']['full_name'].replace('/', ':') + ':' + item['name']
                    license = get_license(item)
                    sleep()
                    unique_users.add(item['repository']['owner']['login'])
                    raw_url = item["html_url"].replace("https://github.com", "https://raw.githubusercontent.com").replace("/blob", "")
                    file_path = os.path.join(python_files_directory, tag)
                    if not os.path.exists(file_path):
                        _ = download_file(raw_url, file_path)
                        codeinfo[tag] = item
                        codeinfo[tag]['commit'] = get_commit_date(item)
                        codeinfo[tag]['license'] = license
                        dump_files(codeinfo)
                    else:
                        print(f"File {file_path} already exists, skipping download")
                        continue


def dump_files(codeinfo):
    with open('codeinfo.json', 'w') as outfile:
        json.dump(codeinfo, outfile)


if __name__ == "__main__":
    python_files_directory = "github_code"
    max_files = 150

    # Read the GitHub token from a text file
    with open("github_token.txt", "r") as file:
        github_token = file.read().strip()

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {github_token}"
    }

    overwrite = False
    if os.path.exists(python_files_directory) and overwrite:
        clear_directory(python_files_directory)
    elif not os.path.exists(python_files_directory):
        os.mkdir(python_files_directory)

    dates = get_datelist()

    if os.path.exists('codeinfo.json'):
        with open('codeinfo.json', 'r') as infile:
            codeinfo = json.load(infile)
        unique_users = {
            item['repository']['owner']['login']
            for item in codeinfo.values()
        }
        print(f"Loaded info for {len(codeinfo)} files, {len(unique_users)} unique users")
    else:
        codeinfo = {}
        unique_users = set()

    try:
        codeinfo = codesearch(dates, codeinfo, unique_users)
    except: # bare except is appropriate here, catching any possible exception
        print("Error occurred, saving files")

    dump_files(codeinfo)
