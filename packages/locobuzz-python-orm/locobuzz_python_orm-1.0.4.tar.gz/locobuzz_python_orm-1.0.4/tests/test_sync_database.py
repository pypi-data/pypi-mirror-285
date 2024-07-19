import urllib

import pytest
from sqlalchemy import text

from database_helper.database.sync_db import SyncDatabase  # Adjust the import path as necessary

username = "admin"
password = "Mysql@12345"
host = "43.205.214.5"
database = "test"

encoded_password = urllib.parse.quote(password)

# Constants for database connection - replace with your details
CONNECTION_STRING = f"mysql+mysqlconnector://{username}:{encoded_password}@{host}/{database}"

@pytest.fixture
def db_instance():
    db = SyncDatabase(CONNECTION_STRING, min_connections=1, max_connections=2)
    with db as instance:
        yield instance
    db.close()


def test_execute_query(db_instance):
    # This should be a query that fetches data. Adjust the SQL to match your schema.
    query = text("SELECT * FROM mstBrands WHERE BrandID = 12163")
    result = db_instance.execute_query(query)
    assert result is not None
    assert len(result) > 0  # Adjust based on expected results


def test_query_dataframe(db_instance):
    # This assumes that pandas is installed and the table has at least one row
    query = text("SELECT * FROM mstBrands WHERE BrandID = 12163")
    df = db_instance.query_dataframe(query)
    assert not df.empty  # This checks that the dataframe is not empty
    assert 'BrandID' in df.columns
