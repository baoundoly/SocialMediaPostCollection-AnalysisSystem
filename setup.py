from setuptools import setup, find_packages

setup(
    name="social-media-nlp",
    version="0.1.0",
    description="Bangla + English NLP analysis module for social media posts",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "nltk==3.9.4",
        "scikit-learn==1.5.2",
        "numpy==2.1.3",
    ],
)
