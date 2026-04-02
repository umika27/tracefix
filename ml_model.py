from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

data = [
    ("No module named numpy", "Dependency Error"),
    ("No module named pandas", "Dependency Error"),
    ("No module named requests", "Dependency Error"),
    ("No module named flask", "Dependency Error"),
    ("ModuleNotFoundError torch", "Dependency Error"),
    ("cannot import name", "Dependency Error"),
    ("ImportError failed to import", "Dependency Error"),
    ("list index out of range", "Index Error"),
    ("IndexError list index out of range", "Index Error"),
    ("tuple index out of range", "Index Error"),
    ("string index out of range", "Index Error"),
    ("unsupported operand type for +", "Type Error"),
    ("TypeError can only concatenate str", "Type Error"),
    ("TypeError int object is not iterable", "Type Error"),
    ("must be str not int", "Type Error"),
    ("takes 1 positional argument but 2 were given", "Type Error"),
    ("KeyError name", "Key Error"),
    ("KeyError missing key in dictionary", "Key Error"),
    ("dictionary key not found", "Key Error"),
    ("SyntaxError invalid syntax", "Syntax Error"),
    ("missing colon in if statement", "Syntax Error"),
    ("unexpected indent", "Syntax Error"),
    ("EOL while scanning string literal", "Syntax Error"),
    ("division by zero", "Math Error"),
    ("ZeroDivisionError", "Math Error"),
    ("No such file or directory", "File Error"),
    ("FileNotFoundError", "File Error"),
    ("Permission denied", "File Error"),
    ("NameError name is not defined", "Name Error"),
    ("AttributeError object has no attribute", "Attribute Error"),
    ("RecursionError maximum recursion depth exceeded", "Recursion Error"),
    ("MemoryError", "Memory Error"),
    ("TimeoutError", "Timeout Error"),
    ("ConnectionError", "Network Error"),
    ("OSError", "OS Error"),
    ("ValueError invalid literal", "Value Error"),
    ("ValueError could not convert string to float", "Value Error"),
]

texts, labels = zip(*data)

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
    ("clf", MultinomialNB(alpha=0.5)),
])
pipeline.fit(texts, labels)


def ml_predict(text: str):
    probs = pipeline.predict_proba([text])[0]
    label = pipeline.classes_[probs.argmax()]
    confidence = probs.max()
    return label, confidence


if __name__ == "__main__":
    test = "No module named matplotlib"
    label, conf = ml_predict(test)
    print(f"Prediction : {label}")
    print(f"Confidence : {round(conf * 100)}%")
