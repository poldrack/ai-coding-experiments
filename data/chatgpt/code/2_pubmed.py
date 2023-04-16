# create python code to create an abstract base class called  AbstractPublication to represent publications, with a method called from_pubmed().  Then create a class called Article that inherits AbstractPublication.  The from_pubmed() method should take in a pubmed record downloaded using the biopython.Entrez tools, and should convert the author list to a variable called authors and the title to a variable called title.  In the main function, perform a pubmed search for the query "cognitive control" and convert each record into an instance of the Publication class, saving them to a dictionary that uses the pubmed ID as the key.

import abc
from Bio import Entrez

class AbstractPublication(abc.ABC):
    @abc.abstractmethod
    def from_pubmed(cls, record):
        pass

class Article(AbstractPublication):
    def __init__(self, authors=None, title=None):
        self.authors = authors
        self.title = title

    @classmethod
    def from_pubmed(cls, record):
        authors = [f"{author['LastName']} {author['Initials']}" for author in record['MedlineCitation']['Article']['AuthorList']]
        title = record['MedlineCitation']['Article']['ArticleTitle']
        return cls(authors=authors, title=title)

def main():
    Entrez.email = "your.email@example.com"
    query = "cognitive control"
    num_results = 10

    search_handle = Entrez.esearch(db="pubmed", term=query, retmax=num_results)
    search_results = Entrez.read(search_handle)
    search_handle.close()

    id_list = search_results["IdList"]
    fetch_handle = Entrez.efetch(db="pubmed", id=id_list, rettype="medline", retmode="xml")
    records = Entrez.read(fetch_handle)["PubmedArticle"]
    fetch_handle.close()

    publications = {}
    for record in records:
        pubmed_id = record["MedlineCitation"]["PMID"]
        article = Article.from_pubmed(record)
        publications[pubmed_id] = article

    return publications

if __name__ == "__main__":
    publications = main()
    for pubmed_id, article in publications.items():
        print(f"PubMed ID: {pubmed_id}\nTitle: {article.title}\nAuthors: {', '.join(article.authors)}\n")
