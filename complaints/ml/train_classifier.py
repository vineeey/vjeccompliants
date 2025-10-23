from __future__ import annotations

import os
from datetime import datetime

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Paths relative to Django project
HERE = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(HERE, "data", "complaints_labeled.csv")
STORE = os.path.join(HERE, "models_storage")
MODEL_PATH = os.path.join(STORE, "category_model.joblib")
VEC_PATH = os.path.join(STORE, "tfidf_vectorizer.joblib")
META_PATH = os.path.join(STORE, "model_version.txt")


def train_and_save():
    """Train a simple TF-IDF + Logistic Regression classifier and save artifacts."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Training data not found at {DATA_PATH}. Please create complaints/data/complaints_labeled.csv"
        )

    df = pd.read_csv(DATA_PATH)
    if "text" not in df.columns or "category" not in df.columns:
        raise ValueError("CSV must have columns: text, category")

    X = df["text"].astype(str).tolist()
    y = df["category"].astype(str).tolist()

    # Separate vectorizer so we can reuse it independently
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2)
    Xv = vec.fit_transform(X)

    clf = LogisticRegression(max_iter=1000, n_jobs=None, class_weight="balanced")
    clf.fit(Xv, y)

    os.makedirs(STORE, exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    joblib.dump(vec, VEC_PATH)

    version = f"tfidf-logreg|{datetime.utcnow().isoformat()}Z|n={len(X)}"
    with open(META_PATH, "w", encoding="utf-8") as f:
        f.write(version)

    return version