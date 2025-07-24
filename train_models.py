# train_models.py
# One-time model training script for Smart Tourism Recommender

import pandas as pd
import numpy as np
import re
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.neighbors import NearestNeighbors
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor

# ----------------- Load & Prepare Dataset -----------------
df = pd.read_csv('cleaned_tourism_dataset.csv')
df.columns = df.columns.str.strip()
df.dropna(subset=['name', 'rating', 'lat', 'lng', 'reviews'], inplace=True)
df.fillna("", inplace=True)

# Combine text fields for TF-IDF analysis
df['combined'] = df['description']
df['tags'] = df['description'].apply(lambda x: re.findall(r'\b\w+\b', str(x.lower())))

# Fallback mood and budget columns
if 'mood' not in df.columns:
    df['mood'] = np.random.choice(['Relaxing', 'Adventurous', 'Romantic', 'Cultural', 'Spiritual'], len(df))
if 'budget' not in df.columns:
    df['budget'] = np.random.choice(['Free', 'Regular', 'Moderate', 'Premium'], len(df))

# ----------------- Model Directory -----------------
os.makedirs("models", exist_ok=True)

# ----------------- TF-IDF Vectorizer -----------------
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['combined'])
joblib.dump(tfidf, 'models/tfidf_vectorizer.pkl')

# ----------------- Content-Based KNN -----------------
content_knn = NearestNeighbors(metric='cosine', algorithm='brute')
content_knn.fit(tfidf_matrix)
joblib.dump(content_knn, 'models/content_knn_model.pkl')

# ----------------- Collaborative Filtering KNN -----------------
mlb = MultiLabelBinarizer()
tag_matrix = mlb.fit_transform(df['tags'])
model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
model_knn.fit(tag_matrix)
joblib.dump(model_knn, 'models/collab_knn_model.pkl')
joblib.dump(mlb, 'models/multilabel_binarizer.pkl')

# ----------------- Mood Classifier -----------------
X_train, X_test, y_train, y_test = train_test_split(df['combined'], df['mood'], test_size=0.2)
mood_model = make_pipeline(TfidfVectorizer(), MultinomialNB())
mood_model.fit(X_train, y_train)
joblib.dump(mood_model, 'models/mood_classifier.pkl')

# ----------------- Budget Regressor -----------------
budget_map = {
    'Free': 0,
    'Regular': 300,
    'Moderate': 500,
    'Premium': 800
}
df['budget_numeric'] = df['budget'].map(budget_map)
X_budget = tfidf_matrix
y_budget = df['budget_numeric']
budget_model = RandomForestRegressor(n_estimators=100, random_state=42)
budget_model.fit(X_budget, y_budget)
joblib.dump(budget_model, 'models/budget_predictor.pkl')

print("All models trained and saved successfully.")
