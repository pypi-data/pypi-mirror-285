import hashlib
import pyodbc

from .Logger import Logger
from .Utils import Utils


LOGGER = Logger(
    name='DatabaseHandler',
    log_to_console=True,
)

UTILS = Utils()


class DatabaseHandler():
    def __init__(
            self,
        ) -> None:
        '''
        This class wil handle all SQL database related stuff.
        '''
        self.retrieved_env_variables = False
        self.testing_connection()


    def _get_env_variables(self):
        '''
        Get the necessary environment variables.
        '''
        if self.retrieved_env_variables:
            return
        
        self.SQL_SERVER_NAME = UTILS.get_env_variable('SQL_SERVER_NAME')
        self.SQL_DATABASE_NAME = UTILS.get_env_variable('SQL_DATABASE_NAME')
        self.SQL_USERNAME = UTILS.get_env_variable('SQL_USERNAME')
        self.SQL_PASSWORD = UTILS.get_env_variable('SQL_PASSWORD')
        self.SQL_DRIVER = UTILS.get_env_variable('SQL_DRIVER')

        self.conn_str = f'DRIVER={self.SQL_DRIVER};SERVER={self.SQL_SERVER_NAME};DATABASE={self.SQL_DATABASE_NAME};UID={self.SQL_USERNAME};PWD={self.SQL_PASSWORD}'

        self.retrieved_env_variables = True


    def testing_connection(self):
        '''
        Testing a connection with the SQL Server.
        '''
        try:
            self._get_env_variables()
            # Establish a connection
            LOGGER.info(f'Testing connection to {self.SQL_SERVER_NAME}')
            with pyodbc.connect(self.conn_str):
                pass
        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def get_values_of_column(
            self,
            table_name: str,
            column_name: str,
        ):
        '''
        Get all values for a given column from a table.
        '''

        query = f"SELECT {column_name} FROM {table_name}"
        results = self.execute_query(query, fetch_results=True)
        results = [row[0] for row in results]
        return results


    def execute_query(
            self,
            query: str,
            params: tuple = (),
            fetch_results: bool = False,
        ):
        '''
        Execute a SQL query to a database.
        '''
        try:
            LOGGER.info('Executing query')
            results = None
            with pyodbc.connect(self.conn_str) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    if fetch_results:
                        # results = cursor.fetchall()
                        columns = [column[0] for column in cursor.description]
                        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    conn.commit()
            return results
        
        except Exception as e:
            LOGGER.error(f'Failed: {e}')
            return None


    def generate_id(
            self,
            value: str,
        ):
        '''
        Generate an unique hash-key.
        '''
        return hashlib.sha1(value.encode('utf-8')).hexdigest()
    

    def truncate_table(
            self,
            table_name: str,
        ):
        '''
        Truncate a table in a SQL database.
        '''
        try:
            LOGGER.info(f'Truncating table: {table_name}')
            query = f'TRUNCATE TABLE dbo.{table_name};'
            self.execute_query(query)

        except Exception as e:
            LOGGER.error(f'Failed: {e}')
            return None


    def upload_to_database_files(
            self,
            id,
            blob_name,
            file_extension,
            file_path_dst,
        ):
        '''
        Insert a row into a table: Files.
        '''
        try:
            LOGGER.info('Inserting single entry into table: Files')
            query = f'''
            INSERT INTO Files (Id, LocationOriginalFile, FileType, LocationText)
            VALUES (?, ?, ?, ?)
            '''
            values = (id, blob_name, file_extension, file_path_dst)
            self.execute_query(query, values)

        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def upload_to_database_webpages(
            self,
            id,
            url,
            url_redirected,
            scrape_succesful,
            file_path_dst,
        ):
        '''
        Insert a row into a table: Webpages.
        '''
        try:
            LOGGER.info('Inserting single entry into table: Webpages')
            query = f'''
            INSERT INTO Webpages (Id, Url, UrlRedirected, ScrapeSuccesful, LocationText)
            VALUES (?, ?, ?, ?, ?)
            '''
            values = (id, url, url_redirected, scrape_succesful, file_path_dst)
            self.execute_query(query, values)

        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def upload_to_database_embeddings(
            self,
            id,
            chunk_id,
            chunk_text,
            file_path_original_file,
        ):
        '''
        Insert a row into a table: Embeddings.
        '''
        try:
            LOGGER.info('Inserting single entry into table: Embeddings')
            query = f'''
            INSERT INTO Embeddings (Id, ChunkId, Text, LocationOriginalFile)
            VALUES (?, ?, ?, ?)
            '''
            values = (id, chunk_id, chunk_text, file_path_original_file)
            self.execute_query(query, values)

        except Exception as e:
            LOGGER.error(f'Failed: {e}')

