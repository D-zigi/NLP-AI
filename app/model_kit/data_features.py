from sklearn.feature_extraction.text import TfidfVectorizer

def tfidf_vectorization(text_data):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(text_data)
    return tfidf_matrix

# tfidf_matrix = tfidf_vectorization([" ".join(processed_texts)])
# print(tfidf_matrix.shape)