from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# -------------------------------
# 1. SAMPLE DATA (REPLACE LATER)
# -------------------------------
data = [
    ("No module named numpy", "Dependency"),
    ("No module named pandas", "Dependency"),
    ("list index out of range", "IndexError"),
    ("IndexError: list index out of range", "IndexError"),
    ("unsupported operand type for +", "TypeError"),
    ("TypeError: can only concatenate str", "TypeError"),
    ("KeyError: 'name'", "KeyError"),
    ("SyntaxError: invalid syntax", "SyntaxError"),
    ("missing colon in if statement", "SyntaxError"),
]

texts, labels = zip(*data)

# -------------------------------
# 2. VECTORIZATION
# -------------------------------
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

# -------------------------------
# 3. MODEL TRAINING
# -------------------------------
model = MultinomialNB()
model.fit(X, labels)

# -------------------------------
# 4. PREDICTION FUNCTION
# -------------------------------
def ml_predict(text: str):
    X_test = vectorizer.transform([text])
    probs = model.predict_proba(X_test)[0]

    label = model.classes_[probs.argmax()]
    confidence = probs.max()

    return label, confidence


# -------------------------------
# 5. TEST (optional)
# -------------------------------
if __name__ == "__main__":
    test_error = "No module named matplotlib"
    label, conf = ml_predict(test_error)

    print("Prediction:", label)
    print("Confidence:", round(conf, 2))