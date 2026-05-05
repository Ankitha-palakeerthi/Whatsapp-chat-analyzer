import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import pickle

data = {
    "text": ["you are stupid", "idiot", "hate you", "love you", "nice", "great"],
    "label": [1,1,1,0,0,0]
}

df = pd.DataFrame(data)

vec = CountVectorizer()
X = vec.fit_transform(df["text"])

model = LogisticRegression()
model.fit(X, df["label"])

pickle.dump(model, open("tox_model.pkl", "wb"))
pickle.dump(vec, open("tox_vectorizer.pkl", "wb"))