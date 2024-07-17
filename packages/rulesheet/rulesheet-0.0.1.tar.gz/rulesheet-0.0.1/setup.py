from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, "README.md")) as f:
    long_description = f.read()

setup(
    name="rulesheet",
    packages=["rulesheet"],
    version="0.0.1",
    description="Convert Business Rules defined in a Google Sheet or CSV to Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Daniel J. Dufour",
    author_email="daniel.j.dufour@gmail.com",
    url="https://github.com/officeofperformancemanagement/rulesheet",
    download_url="https://github.com/officeofperformancemanagement/rulesheet/tarball/download",
    keywords=["business", "data", "python", "rules"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
)
