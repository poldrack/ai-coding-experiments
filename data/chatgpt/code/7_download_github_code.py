# RP: Create python code that uses the github api to download the 100 most recently committed python files.
# GPT4: To download the 100 most recently committed Python files using the GitHub API, you can use the requests library in Python. Make sure you have it installed by running pip install requests. You will also need a GitHub personal access token, which you can create by following these steps: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
# Replace your_github_token with your personal access token in the code below:
# followed up with: please only download one file from each user, so that the 100 files come from 100 unique users.
# followed up with:please make two changes.  first, read in the github token from a text file called "github_token.txt".  Second, create a variable called sleeptime that is set to 10 seconds. then place a time.sleep command after each call to the github api
# followed up with: please add a call to time.sleep after the download_file call in the main block
# followed with: if python_files exists, please delete all existing python files before running.

import requests
import base64
import os
import time

# Read the GitHub token from a text file
with open("github_token.txt", "r") as file:
    github_token = file.read().strip()

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"token {github_token}"
}

def download_file(file_url, file_path):
    response = requests.get(file_url, headers=headers)
    with open(file_path, 'wb') as file:
        file.write(response.content)

def get_recent_python_files(page_number):
    search_url = f"https://api.github.com/search/code?q=language:python+extension:py+in:path&sort=indexed&order=desc&per_page=100&page={page_number}"
    response = requests.get(search_url, headers=headers)
    return response.json()

def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

python_files_directory = "python_files"

if os.path.exists(python_files_directory):
    clear_directory(python_files_directory)
else:
    os.mkdir(python_files_directory)

page_number = 1
files_downloaded = 0
unique_users = set()
sleeptime = 10

while files_downloaded < 100:
    recent_python_files = get_recent_python_files(page_number)
    for item in recent_python_files["items"]:
        user_login = item['repository']['owner']['login']
        if user_login not in unique_users:
            unique_users.add(user_login)
            raw_url = item["html_url"].replace("https://github.com", "https://raw.githubusercontent.com").replace("/blob", "")
            file_path = os.path.join(python_files_directory, f"{item['repository']['full_name'].replace('/', '_')}_{item['name']}")
            download_file(raw_url, file_path)
            time.sleep(sleeptime)  # Sleep for 10 seconds after downloading each file
            files_downloaded += 1

            if files_downloaded >= 100:
                break

    page_number += 1
    time.sleep(sleeptime)  # Sleep for 10 seconds after each call to the GitHub API
