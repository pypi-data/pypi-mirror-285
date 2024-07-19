from sqlalchemy import create_engine, MetaData, select
from sqlalchemy.engine import Engine
from sqlalchemy.sql import Select


class SyncDatabase:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SyncDatabase, cls).__new__(cls)
        return cls._instance

    def __init__(self, connection_string: str, pool_size=5, max_overflow=10):
        if not hasattr(self, "initialized"):
            self.connection_string = connection_string
            self.pool_size = pool_size
            self.max_overflow = max_overflow
            self.engine: Engine = None
            self.connection = None
            self.tables = {}
            self.initialized = True

    def __enter__(self):
        if not self.connection:
            self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        # if self.connection:
        #     self.disconnect()
        pass

    def connect(self):
        try:
            self.engine = create_engine(
                self.connection_string,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow
            )
            self.connection = self.engine.connect()
            print('Database connected')
        except Exception as e:
            print(f"Error connecting to the database: {e}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print('Database disconnected')
        if self.engine:
            self.engine.dispose()

    def initialize_tables(self, table_names):
        try:
            if not self.connection:
                self.connect()
            metadata = MetaData()
            for table_name in table_names:
                if table_name not in self.tables:
                    metadata.reflect(bind=self.engine, only=[table_name])
                    self.tables[table_name] = metadata.tables[table_name]
        except Exception as e:
            raise Exception(f"Error in initialize tables : {e}")

    def execute_query(self, query):
        try:
            if not self.connection:
                self.connect()
            result = self.connection.execute(query)
            return result
        except Exception as e:
            raise Exception(f"Error in query execution : {e}")


