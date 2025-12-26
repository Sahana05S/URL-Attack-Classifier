
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import joblib

df = pd.DataFrame({
    "url": [
        "/login?id=1' OR '1'='1",
        "/search?q=<script>alert(1)</script>",
        "/download?file=../../etc/passwd",
        "/ping?host=8.8.8.8;cat /etc/shadow",
        "/home"
    ],
    "label": [
        "SQL Injection",
        "XSS",
        "Directory Traversal",
        "Command Injection",
        "Normal"
    ]
})

vec = TfidfVectorizer(analyzer="char", ngram_range=(3,5))
X = vec.fit_transform(df["url"])
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, df["label"])

joblib.dump((vec, model), "url_model.pkl")
print("Model trained")
