from setuptools import setup, find_packages
from typing import List
import os

# with open('README.md', encoding='utf-8') as f:
#     long_description = f.read()   

long_description ="""**MongoDB Automation**

**Description**

MongoDB Automation is a Python package designed to simplify the interaction with MongoDB databases. This package provides a set of tools to manage MongoDB operations like creating clients, databases, collections, and inserting records. It is designed to streamline the process of interacting with MongoDB, especially for data scientists and developers who need to automate database operations.

**Features**

- **Create MongoDB Client**: Easily create a MongoDB client to connect to your MongoDB server.
- **Create Database**: Automatically create and manage databases.
- **Create Collection**: Create and manage collections within a database.
- **Insert Record**: Insert single or multiple records into a collection.
- **Bulk Insert**: Insert records from CSV or Excel files into a collection.

**Installation**

You can install the package using pip:

```bash
pip install mongodb-automation
```

**License**

This project is licensed under the MIT License - see the LICENSE file for details.

**Author**

Rohit Motwani
"""

__version__ = "0.0.4"
REPO_NAME = "MongoDB-Python-Package"
PKG_NAME= "mongodb-databaseautomation131313" # should be unique
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