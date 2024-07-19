from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import MetaData, select, func, and_
from sqlalchemy.sql import Select
import asyncio


class AsyncDatabase:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AsyncDatabase, cls).__new__(cls)
        return cls._instance

    def __init__(self, connection_string: str, pool_size=5, max_overflow=10):
        if not hasattr(self, "initialized"):
            self.connection_string = connection_string
            self.pool_size = pool_size
            self.max_overflow = max_overflow
            self.engine: AsyncEngine = None
            self.tables = {}
            self.is_connected = False
            self.initialized = True

    async def connect(self):
        try:
            self.engine = create_async_engine(
                self.connection_string,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow
            )
            print('Database connected')
            self.is_connected = True
        except Exception as e:
            print(f"Error connecting to the database: {e}")

    async def disconnect(self):
        if self.engine:
            await self.engine.dispose()
            print('Database disconnected')
            self.is_connected = False

    async def initialize_tables(self, table_names):
        try:
            if not self.is_connected:
                self.connect()
            metadata = MetaData()
            async with self.engine.connect() as connection:
                for table_name in table_names:
                    if table_name not in self.tables:
                        await connection.run_sync(metadata.reflect, only=[table_name])
                        self.tables[table_name] = metadata.tables[table_name]
        except Exception as e:
            raise Exception(f"Error in initialize tables : {e}")

        print("Tables initialized:", list(self.tables.keys()))

    async def execute_query(self, query):
        try:
            if not self.is_connected:
                self.connect()
            async with self.engine.connect() as connection:
                result = await connection.execute(query)
                await connection.commit()  # Commit for update/insert/delete queries
                if isinstance(query, Select):
                    return result.fetchall()  # Return all rows for select queries asynchronously
                else:
                    return result.rowcount  # Return the number of rows affected for update/insert/delete queries
        except Exception as e:
            raise Exception(f"Error in query execution : {e}")

    async def __aenter__(self):
        if not self.is_connected:
            await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        # Do not disconnect on exit to keep the connection open
        pass

