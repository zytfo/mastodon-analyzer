import string
from typing import List

import nltk
from sklearn.feature_extraction.text import TfidfVectorizer

# define a stemmer
stemmer = nltk.stem.porter.PorterStemmer()

# get punctuation characters
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)


# define a stemming function
def stem_tokens(tokens: List[str]):
    return [stemmer.stem(item) for item in tokens]


# define a normalizer function using stemmer and remove punctuation characters
def normalize(text: str):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))


# define a Tf-Idf vectorizer
vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words="english")


# calculate a cosine similarity for two text
def calculate_cosine_similarity_between_two_statuses(status_content_1: str, status_content_2: str):
    tfidf = vectorizer.fit_transform([status_content_1, status_content_2])
    return ((tfidf * tfidf.T).A)[0, 1]
