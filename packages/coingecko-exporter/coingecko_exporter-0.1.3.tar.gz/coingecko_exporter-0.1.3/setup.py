
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="coingecko_exporter",  
    version="0.1.3",
    description="A package to export bulk data from the CoinGecko API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Matt Maximo",
    author_email="matt@pioneerdigital.org",
    url="https://github.com/MattMaximo/artemis_py",
    packages=find_packages(),
    install_requires=[
        "httpx",
        "pandas",
        "duckdb",
        "aiolimiter",
        "httpx",
        "pyarrow",
        "fastparquet"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)