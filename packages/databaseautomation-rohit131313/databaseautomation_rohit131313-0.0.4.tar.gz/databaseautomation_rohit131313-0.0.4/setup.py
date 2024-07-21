from setuptools import setup, find_packages
from typing import List
import os

with open(os.path.join(os.path.dirname(__file__), 'Readme.md'), encoding='utf-8') as f:
    long_description = f.read()   
    long_description_content_type='text/markdown',

__version__ = "0.0.4"
REPO_NAME = "Mongo-Python-Package"
PKG_NAME= "databaseautomation-rohit131313"
AUTHOR_USER_NAME = "Rohit131313"
AUTHOR_EMAIL = "abc123@gmail.com"

setup(
    name=PKG_NAME,
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description="A python package for connecting with database.",
    long_description=long_description,
    long_description_content="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    )