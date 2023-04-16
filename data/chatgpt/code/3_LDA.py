import nltk
import string
from Bio import Entrez
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

nltk.download('stopwords')
nltk.download('wordnet')

def download_abstracts(query, num_results=1000, email="your.email@example.com"):
    Entrez.email = email
    search_handle = Entrez.esearch(db="pubmed", term=query, retmax=num_results)
    search_results = Entrez.read(search_handle)
    search_handle.close()

    id_list = search_results["IdList"]
    fetch_handle = Entrez.efetch(db="pubmed", id=id_list, rettype="medline", retmode="xml")
    records = Entrez.read(fetch_handle)["PubmedArticle"]
    fetch_handle.close()

    abstracts = []
    for record in records:
        try:
            abstract = record["MedlineCitation"]["Article"]["Abstract"]["AbstractText"][0]
            abstracts.append(abstract)
        except KeyError:
            pass

    return abstracts

def preprocess_abstracts(abstracts):
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()

    preprocessed_abstracts = []
    for abstract in abstracts:
        tokens = nltk.word_tokenize(abstract.lower())
        cleaned_tokens = [
            lemmatizer.lemmatize(token) for token in tokens
            if token not in stop_words
            and token not in string.punctuation
            and not token.isnumeric()
        ]
        preprocessed_abstracts.append(" ".join(cleaned_tokens))

    return preprocessed_abstracts

def lda_topic_modeling(abstracts, n_topics=10, n_top_words=10):
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words="english")
    tf_matrix = vectorizer.fit_transform(abstracts)

    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(tf_matrix)

    feature_names = vectorizer.get_feature_names_out()
    for topic_idx, topic in enumerate(lda.components_):
        print(f"Topic #{topic_idx + 1}:")
        print(" ".join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]))

if __name__ == "__main__":
    query = "cognitive control"
    num_results = 1000
    email = "poldrack@stanford.edu"

    abstracts = download_abstracts(query, num_results, email)
    preprocessed_abstracts = preprocess_abstracts(abstracts)
    lda_topic_modeling(preprocessed_abstracts)
