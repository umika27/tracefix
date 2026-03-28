import json
import random
import traceback

error_snippets = [
    "x = int('abc')",
    "print(a)",
    "1/0",
    "import nonexistingmodule",
    "x = [1,2,3]\nprint(x[5])",
    "d = {'a':1}\nprint(d['b'])",
    "len(5)",
    "open('nofile.txt')",
    "def f():\n  return x\nf()",
    "x = None\nx.upper()",
    "for i in range(5)\n    print(i)",  # syntax error
    "if True print('hi')",             # syntax error
]

dataset = []

def generate_sample():
    code = random.choice(error_snippets)
    try:
        exec(code)
    except Exception as e:
        return {
            "code": code,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "category": categorize(type(e).__name__)
        }

def categorize(error_type):
    mapping = {
        "SyntaxError": "syntax",
        "IndentationError": "syntax",
        "NameError": "runtime",
        "TypeError": "runtime",
        "ValueError": "runtime",
        "IndexError": "runtime",
        "KeyError": "runtime",
        "ZeroDivisionError": "runtime",
        "AttributeError": "runtime",
        "ModuleNotFoundError": "import",
        "FileNotFoundError": "file"
    }
    return mapping.get(error_type, "other")

# generate 10K samples
while len(dataset) < 10000:
    sample = generate_sample()
    if sample:
        dataset.append(sample)

with open("python_errors_10k.json", "w") as f:
    json.dump(dataset, f, indent=2)

print("Dataset created: python_errors_10k.json")