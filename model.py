import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
import joblib
from db import Fake_news_database

class Fake_news_detector:
    def __init__(self, model_path, vectorizer_path, database: Fake_news_database):
        self.db = database
        self.model = model_path
        self.vectorizer = vectorizer_path
        self.model_update = None
        self.vectorizer_update = None
        self.load_model_and_vectorizer()

    def load_model_and_vectorizer(self):
        self.model_update = joblib.load(self.model)
        self.vectorizer_update = joblib.load(self.vectorizer)

    def predict_label(self, title, text):
        # Vectorize the input text
        input_text = f'{title} {text}'
        vec_input_text = self.vectorizer_update.transform([input_text])
        prediction = self.model_update.predict(vec_input_text)[0]
        return prediction
    
    def predict_label_one(self, input):
        # Vectorize the input text
        input_text = f'{input}'
        vec_input_text = self.vectorizer_update.transform([input_text])
        prediction = self.model_update.predict(vec_input_text)[0]
        return prediction
    
    def train_model(self, file):
        df = pd.read_csv(file)

        df['News_Title'].fillna('', inplace=True)
        df['News_Text'].fillna('', inplace=True)

        X = df['News_Title'] + ' ' + df['News_Text']
        y = df['Label']

        tfidf_vectorizer = TfidfVectorizer(max_df=0.75)
        X_vectorized = tfidf_vectorizer.fit_transform(X)

        pac = PassiveAggressiveClassifier(max_iter=50)
        pac.fit(X_vectorized, y)

        # Save the model and vectorizer
        joblib.dump(pac, self.model)
        joblib.dump(tfidf_vectorizer, self.vectorizer)
        self.load_model_and_vectorizer()
