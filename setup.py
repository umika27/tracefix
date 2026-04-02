from setuptools import setup, find_packages

setup(
    name="tracefix",
    version="1.0.0",
    description="Hybrid ML + rule-based Python error analyzer",
    py_modules=["cli", "engine", "ml_model", "parser", "memory", "display", "watcher", "runner"],
    install_requires=[
        "typer>=0.9.0",
        "scikit-learn>=1.3.0",
    ],
    entry_points={
        "console_scripts": [
            "tracefix=cli:app",
        ],
    },
    python_requires=">=3.9",
)
