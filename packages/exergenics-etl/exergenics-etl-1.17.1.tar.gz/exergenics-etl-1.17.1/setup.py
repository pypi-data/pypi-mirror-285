from setuptools import find_packages, setup

# with open("app/Readme.md", "r") as f:
#     long_description = f.read()

setup(
    name="exergenics-etl",
    version="v1.17.1",
    description="Exergenics shared Data ETL functions",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description="### Exergenics ETL Pytho package",
    long_description_content_type="text/markdown",
    url="",
    author="Nobel Wong",
    author_email="nobel.wong@exergenics.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent"
    ],
    install_requires=["exergenics >= 2.0.0",
                      "DateTime == 5.1",
                      "pandas >= 1.4.0",
                      "PyMySQL == 1.0.2",
                      "pytz == 2022.7.1",
                      "SQLAlchemy == 1.4.46",
                      "python-dotenv == 1.0.0",
                      "openpyxl == 3.0.10",
                      "Levenshtein == 0.21.0",
                      "regex == 2022.10.31",
                      "dateparser == 1.1.5",
                      "zipp == 3.15.0",
                      "sklearn == 0.0",
                      "plotly == 5.4.0",
                      "eng==0.1.1"],
    extras_require={
        "dev": ["pytest >= 7.0", "twine >= 4.0.2", "bump == 1.3.2"],
    },
    python_requires=">=3.8.10"
)
