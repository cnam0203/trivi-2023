import psycopg2
from psycopg2.extras import DictCursor, execute_values
from psycopg2 import sql
import pandas as pd
import numpy as np

class Database:
    """PostgreSQL Database class"""

    def __init__(
            self,
            POSTGRES_HOST,
            POSTGRES_USERNAME,
            POSTGRES_PASSWORD,
            POSTGRES_PORT,
            POSTGRES_NAME,

        ):
        self.host = POSTGRES_HOST
        self.username = POSTGRES_USERNAME
        self.password = POSTGRES_PASSWORD
        self.port = POSTGRES_PORT
        self.dbname = POSTGRES_NAME
        self.conn = None
        self.cache = {}

    def connect(self):
        """Connect to a PostgreSQL database"""
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(
                    host=self.host,
                    user=self.username,
                    password=self.password,
                    port=self.port,
                    dbname=self.dbname
                )
                # self.conn.autocommit = True
            except psycopg2.DatabaseError as e:
                raise e
            # finally:
                # LOGGER.info('Connection Postgres opened successfully.')

    def select_rows_dict(self, query):
        """Run a SQL query to select rows from table"""
        self.connect()
        records = []
        columns = []

        try:
            with self.conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(query)
                records = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                cur.close()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)


        df  = pd.DataFrame(records, columns=columns)
        return df
    
    def select_rows(self, query):
        """Run a SQL query to select rows from table"""
        self.connect()

        try:
            with self.conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(query)
                records = cur.fetchall()
                cur.close()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)

    
        return records
    
    def select_first_row(self, query):
        """Run a SQL query to select rows from table"""
        self.connect()

        try:
            with self.conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(query)
                records = cur.fetchall()
                cur.close()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)

        if (records[0][0] == None):
            return 0
        return records[0][0]