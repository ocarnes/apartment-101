import pandas as pd
import numpy as np
import spacy
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from string import punctuation
from sklearn.model_selection import train_test_split
nlp = spacy.load('en')
import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning, module='.*/IPython/.*')
warnings.filterwarnings('ignore', category=DeprecationWarning, module='pyLDAvis')

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# Create custom stoplist
STOPLIST = set(list(ENGLISH_STOP_WORDS) + ["n't", "'s", "'m", "ca", "'", "'re", "getty_images", "getty images"])
PUNCT_DICT = {ord(punc): None for punc in punctuation if punc not in ['_', '*']}


def clean_article(article):
    doc = nlp(article)

    # Let's merge all of the proper entities
    for ent in doc.ents:
        if ent.root.tag_ != 'DT':
            ent.merge(ent.root.tag_, ent.text, ent.label_)
        else:
            # Keep entities like 'the New York Times' from getting dropped
            ent.merge(ent[-1].tag_, ent.text, ent.label_)

    # Part's of speech to keep in the result
    pos_lst = ['ADJ', 'ADV', 'NOUN', 'PROPN', 'VERB'] # NUM?

    tokens = [token.lemma_.lower().replace(' ', '_') for token in doc if token.pos_ in pos_lst]

    return ' '.join(token for token in tokens if token not in STOPLIST).replace("'s", '').translate(PUNCT_DICT)


if __name__ == '__main__':

    text = clean_article(article).values.to_list()

max_features = 5000
tf_vectorizer = CountVectorizer(max_df=0.95, min_df=3,
                            max_features=max_features,
                            stop_words='english')
tf = tf_vectorizer.fit_transform(text)

n_topics = 33
lda_model = LatentDirichletAllocation(n_components=n_topics, max_iter=5,
                                  learning_method='online',
                                  learning_offset=50.,
                                  random_state=0)

lda_model.fit(tf)
