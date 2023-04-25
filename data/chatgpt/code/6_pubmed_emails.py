import re
import requests
from Bio import Entrez
from bs4 import BeautifulSoup
from crossref.restful import Works
import pandas as pd


# Replace with your email address, Google API Key, and Custom Search Engine ID
Entrez.email = None
google_api_key = None
custom_search_engine_id = None

def get_pubmed_doi(record):
    doi = None
    for j in record['PubmedData']['ArticleIdList']:
        if j.attributes['IdType'] == 'doi':
            doi = str(j).lower().replace('http://dx.doi.org/', '')
    return doi

def search_pubmed(query, retmax=10):
    handle = Entrez.esearch(db="pubmed", term=query, retmax=retmax)
    record = Entrez.read(handle)
    return record["IdList"]

def get_article_data(pmid):
    handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml")
    raw_record = Entrez.read(handle)
    if not raw_record:
        return None, None

    if "PubmedArticle" not in raw_record:
        return None, None

    record = raw_record["PubmedArticle"][0]
    doi = get_pubmed_doi(record)

    try:
        first_author = record["MedlineCitation"]["Article"]["AuthorList"][0]
        last_author = record["MedlineCitation"]["Article"]["AuthorList"][-1]
    except (KeyError, IndexError):
        first_author = None
        last_author = None

    return first_author, last_author, doi

def google_search(query):
    url = f"https://www.googleapis.com/customsearch/v1?key={google_api_key}&cx={custom_search_engine_id}&q={query}"
    response = requests.get(url)
    results = response.json()

    return results.get("items", [])

def extract_email_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        email_addresses = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', soup.get_text())
        return email_addresses
    except requests.exceptions.RequestException:
        return []

def get_affiliation(record):
    affiliation = ''
    if "AffiliationInfo" in record and record["AffiliationInfo"] is not None and len(record["AffiliationInfo"]) > 0:
        affiliation = record["AffiliationInfo"][0]["Affiliation"]

    return affiliation

if __name__ == "__main__":

    retmax = 10
    query = '"cognitive control"'
    pmids = search_pubmed(query, retmax=retmax)

    all_results = []

    for pmid in pmids:
        first_author, last_author, doi = get_article_data(pmid)

        work = Works().doi(doi)

        if first_author and last_author:
            first_name = f"{first_author.get('ForeName', '')} {first_author.get('LastName', '')}"
            last_name = f"{last_author.get('ForeName', '')} {last_author.get('LastName', '')}"

            first_results = google_search(first_name + " " + get_affiliation(first_author))
            last_results = google_search(last_name + " " + get_affiliation(last_author)) 

            first_emails = []
            last_emails = []

            for result in first_results:
                first_emails.extend(extract_email_from_url(result["link"]))
                if first_emails:
                    break

            for result in last_results:
                last_emails.extend(extract_email_from_url(result["link"]))
                if last_emails:
                    break

            first_emails = list(set(first_emails))
            last_emails = list(set(last_emails))

            print(f"PMID: {pmid}")
            print(f"title: {work['title'][0]}")
            print(f"First Author: {first_name}")
            print(f"First Author Emails: {first_emails}")
            print(f"Last Author: {last_name}")
            print(f"Last Author Emails: {last_emails}")
            if work is not None:
                print('cited by', work['is-referenced-by-count'])
                cites = work['is-referenced-by-count']
            else:
                print('no crossref entry')
                cites = None
            print("-" * 20)
            all_results.append([pmid, doi, work['title'], first_name, first_emails, last_name, last_emails, cites])

df = pd.DataFrame(all_results, columns=['pmid', 'doi', 'title', 'first_author', 'first_author_emails', 'last_author', 'last_author_emails', 'cites'])
df.to_csv('pubmed_emails.csv', index=False)
