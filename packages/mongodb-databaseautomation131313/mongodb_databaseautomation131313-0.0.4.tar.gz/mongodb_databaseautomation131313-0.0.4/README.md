**MongoDB Automation**

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

**Usage**

Here's an example of how to use the MongoDB Automation package:

```bash
from mongodb_automation import mongo_operation

# Initialize the mongo_operation class
mongo = mongo_operation(client_url='your_mongo_client_url', database_name='your_database_name', collection_name='your_collection_name')

# Insert a single record
record = {"name": "John", "age": 30}
mongo.insert_record(record, collection_name='your_collection_name')

# Bulk insert from a CSV file
mongo.bulk_insert(datafile='path_to_your_csv_file.csv', collection_name='your_collection_name')
```

**Source Code**

```bash
from typing import Any
import os
import pandas as pd
import pymongo
import json
from ensure import ensure_annotations
from pymongo.mongo_client import MongoClient

class mongo_operation:
    __collection=None  # private/protected variable
    __database=None

    def __init__(self, client_url: str, database_name: str, collection_name: str = None):
        self.client_url = client_url
        self.database_name = database_name
        self.collection_name = collection_name

    def create_mongo_client(self, collection=None):
        client = MongoClient(self.client_url)
        return client

    def create_database(self, collection=None):
        if mongo_operation.__database == None:
            client = self.create_mongo_client(collection)
            self.database = client[self.database_name]
        return self.database

    def create_collection(self, collection=None):
        if mongo_operation.__collection == None:
            database = self.create_database(collection)
            self.collection = database[self.collection_name]
            mongo_operation.__collection = collection

        if mongo_operation.__collection != collection:
            database = self.create_database(collection)
            self.collection = database[self.collection_name]
            mongo_operation.__collection = collection

        return self.collection

    def insert_record(self, record: dict, collection_name: str) -> Any:
        if type(record) == list:
            for data in record:
                if type(data) != dict:
                    raise TypeError("record must be in the dict")
            collection = self.create_collection(collection_name)
            collection.insert_many(record)
        elif type(record) == dict:
            collection = self.create_collection(collection_name)
            collection.insert_one(record)

    def bulk_insert(self, datafile, collection_name: str = None):
        self.path = datafile

        if self.path.endswith('.csv'):
            dataframe = pd.read_csv(self.path, encoding='utf-8')

        elif self.path.endswith(".xlsx"):
            dataframe = pd.read_excel(self.path, encoding='utf-8')

        datajson = json.loads(dataframe.to_json(orient='records'))
        collection = self.create_collection()
        collection.insert_many(datajson)
```

**License**

This project is licensed under the MIT License - see the LICENSE file for details.

**Author**

Rohit Motwani