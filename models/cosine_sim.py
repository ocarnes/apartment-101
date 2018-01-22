import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

def cos_sim_recs(selection, df, index_name, n=5):
    apartment = df.iloc[selection]
    # ss = StandardScaler()
    # X = ss.fit_transform(apartment.values.reshape(1,-1))
    # cs = cosine_similarity(X, df)
    cs = cosine_similarity(apartment.values.reshape(1,-1), df)
    n = n+1
    rec_index = np.argsort(cs)[0][-n:][::-1][1:]
    recommendations = []
    for rec in rec_index:
        recommendations.append(index_name[rec])
    return recommendations

def selection_input(df, selection):
    df['index_name'] = df['name'] + ' - '+df['sq_ft'].map(str) + ' sqft'
    index_name = df['index_name'].values
    df.drop('index_name', axis=1, inplace = True)
    df.drop('description', axis=1, inplace = True)
    df.drop('url', axis=1, inplace = True)
    df.drop('name', axis=1, inplace = True)

    for idx, name in enumerate(index_name):
        if name == selection:
            selection_idx = idx
    return df, selection_idx, index_name

if __name__ == '__main__':
    df = pd.read_pickle('../data/df_apartment_1_22_2018.pkl')
    selection = 'Welton Park - 576 sqft'
    df_alt, selection_idx, index_name = selection_input(df, selection)
    recommendations = cos_sim_recs(selection_idx, df_alt, index_name, n=5)
