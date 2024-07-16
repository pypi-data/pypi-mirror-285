import urllib

import pytest
from sqlalchemy import text

from database_helper.database.async_db import AsyncDatabase  # Adjust the import according to your project structure

username = "admin"
password = "Mysql@12345"
host = "43.205.214.5"
database = "test"

encoded_password = urllib.parse.quote(password)

# Constants for database connection - replace with your details
CONNECTION_STRING = f"mysql+aiomysql://{username}:{encoded_password}@{host}/{database}"


@pytest.fixture
async def db_instance():
    # Setup the database instance
    db = AsyncDatabase(CONNECTION_STRING, min_connections=1, max_connections=2)
    await db.__aenter__()
    try:
        yield db
    finally:
        # Ensure the exit is handled to close the session and connection properly
        await db.__aexit__(None, None, None)
        await db.close()


@pytest.mark.asyncio
async def test_direct_db_use():
    db = AsyncDatabase(CONNECTION_STRING, min_connections=1, max_connections=2)
    async with db as instance:
        query = text("SELECT * FROM mstBrands WHERE BrandID = 12163")
        result = await instance.execute_query(query)
        assert result is not None
        assert len(result) > 0


# @pytest.mark.asyncio
# async def test_execute_query(db_instance):
#     # This should be a query that fetches data. Adjust the SQL to match your schema.
#     query = text("SELECT * FROM some_table WHERE id = 1")
#     result = await db_instance.execute_query(query)
#     assert result is not None
#     assert len(result) > 0  # Adjust based on expected results
#     # For example, if you know the specific content to be returned:
#     assert result[0][0] == 1  # Check the first column of the first row if it should be 1
#
#
# @pytest.mark.asyncio
# async def test_query_dataframe(db_instance):
#     # This assumes that pandas is installed and the table has at least one row
#     query = text("SELECT * FROM some_table")
#     df = await db_instance.query_dataframe(query)
#     assert not df.empty
#     assert 'expected_column_name' in df.columns  # Replace 'expected_column_name' with your actual column name
#