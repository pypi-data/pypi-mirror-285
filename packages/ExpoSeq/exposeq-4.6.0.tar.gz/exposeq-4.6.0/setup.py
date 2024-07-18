from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = "ExpoSeq",
    version = "4.3.3",
    description = "A pacakge which provides various ways to analyze NGS data from phage display campaigns",
    long_description=long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/nilshof01/ExpoSeq",
    author = "Nils Hofmann",
    author_email = "nilhof01@gmail.com",
    license = "LICENCE",
    packages = find_packages(where = "src"),
    package_data={
        "ExpoSeq": ["settings/*","settings/*" "test_data/test_files/*", "test_data/*"]
    },
    exclude_package_data={
        '': ['ExpoSeq/test_data/test_files/Chris_main_df.csv']
    },
    install_requires = [
                        "numpy==1.23.5",
                        "pandas==1.5.3",
                        "matplotlib==3.7.3",
                        "scipy>=1.11.3",
                        "seaborn==0.12.2",
                        "logomaker==0.8",
                        "editdistance==0.6.2",
                        "networkx==3.1",
                        "PyQt5==5.15.7",
                        "scikit-learn>=1.2.1",
                        "biopython==1.80",
                        "sgt==2.0.3",
                        "openpyxl",
                        "python-louvain==0.16",
                        "pandasai==1.3.3",
                        "markdown",
                        "torch==2.1.0",
                        "sentencepiece==0.1.99",
                        "transformers==4.34.1",
                        "squarify==0.4.3",
                        "tabulate==0.9.0",
                        "PyQt5==5.15.7",
                        ],
    python_requires=">=3.8",
    package_dir = {"": "src"},

)
