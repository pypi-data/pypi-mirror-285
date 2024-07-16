# Database ORM package

This package provide a way to implement the ORM using the sync and aysnc way and easily used with the 
## Installation

Install the package using pip:

```sh
pip install locobuzz-python-orm
pip install locobuzz-python-orm[dataframe]
```
# Usage
## Basic Usage
```python
connection_string = f"mssql+aioodbc://{username}:{encoded_password}@{host}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
db = AsyncDatabase(connection_string, min_connections=1, max_connections=1)
query = text("SELECT * FROM mstCategories")

async with db as database:
    result = await database.query_tuples(query)
    print(result)  # List of tuples output


```