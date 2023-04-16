# generate a python function that takes in a piece of English text and performs linguistic analysis on it, returning values for sentiment analysis (positive/negative) and for linguistic complexity.
# please also include the L2SCA and coh-metrix measures of complexity.
# -- seems to have used a python package that doesn't actually exist! (coh-py)
# the coh-py library that you recommended doesn't actually exist. 

import nltk
import syllables
from nltk.sentiment import SentimentIntensityAnalyzer
from textstat import flesch_reading_ease
from nltk.tokenize import sent_tokenize, word_tokenize
nltk.download('vader_lexicon')
nltk.download('punkt')

def linguistic_analysis(text):
    # Sentiment analysis
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)
    
    # Determine if the sentiment is positive or negative
    if sentiment['compound'] >= 0.05:
        sentiment_result = 'positive'
    elif sentiment['compound'] <= -0.05:
        sentiment_result = 'negative'
    else:
        sentiment_result = 'neutral'
    
    # Linguistic complexity
    flesch = flesch_reading_ease(text)
    
    # L2SCA complexity
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    num_syllables = sum(syllables.estimate(word) for word in words)
    num_words = len(words)
    num_sentences = len(sentences)
    
    l2sca_complexity = {
        'lexical_density': len(set(words)) / num_words,
        'syntactic_complexity': num_words / num_sentences,
        'mean_word_length': sum(len(word) for word in words) / num_words,
        'mean_syllable_count': num_syllables / num_words
    }
    
    return sentiment_result, flesch, l2sca_complexity

# Example usage
text = "I love this product! It's amazing and so easy to use."
sentiment, flesch, l2sca = linguistic_analysis(text)
print("Sentiment:", sentiment)
print("Flesch Reading Ease:", flesch)
print("L2SCA complexity:", l2sca)
