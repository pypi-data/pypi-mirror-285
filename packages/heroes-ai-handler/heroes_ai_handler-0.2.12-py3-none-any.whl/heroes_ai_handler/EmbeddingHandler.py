import json
import requests
import weaviate
import tiktoken
from langchain.text_splitter import TokenTextSplitter
import uuid
from weaviate import WeaviateClient
from weaviate.classes.config import Property, DataType

from .Logger import Logger
from .BlobConversionHandler import BlobConversionHandler
from .FileHandler import FileHandler
from .DatabaseHandler import DatabaseHandler
from .Utils import Utils


LOGGER = Logger(
    name='EmbeddingHandler',
    log_to_console=True,
)

UTILS = Utils()


class EmbeddingHandler:
    def __init__(
            self,
        ) -> WeaviateClient:
        self.retrieved_env_variables = []


    def _get_env_variables(
            self,
            variable_type: str,  # ['azure_openai', 'weaviate_cluster']
        ):
        '''
        Get the necessary environment variables.
        '''
        if variable_type in self.retrieved_env_variables:
            return
        
        if variable_type == 'azure_openai' and 'azure_openai' not in self.retrieved_env_variables:
            self.AZURE_OPENAI_ENDPOINT = UTILS.get_env_variable('AZURE_OPENAI_ENDPOINT')
            self.AZURE_OPENAI_API_KEY = UTILS.get_env_variable('AZURE_OPENAI_API_KEY')
            self.AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME = UTILS.get_env_variable('AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME')
            self.AZURE_OPENAI_API_VERSION = UTILS.get_env_variable('AZURE_OPENAI_API_VERSION')
            self.retrieved_env_variables.append('azure_openai')

        if variable_type == 'weaviate_cluster' and 'weaviate_cluster' not in self.retrieved_env_variables:
            self.WEVIATE_CLUSTER_ENDPOINT = UTILS.get_env_variable('WEVIATE_CLUSTER_ENDPOINT')
            self.WEVIATE_CLUSTER_API_KEY = UTILS.get_env_variable('WEVIATE_CLUSTER_API_KEY')
            self.retrieved_env_variables.append('weaviate_cluster')


    def get_weaviate_client(
            self
        ) -> weaviate.WeaviateClient:
        '''
        Get a Weaviate client instance. \\
        Use this purely for experimental puposes and be sure to close the instance by yourself!
        '''
        try:
            self._get_env_variables(variable_type='weaviate_cluster')
            return weaviate.connect_to_wcs(
                cluster_url = self.WEVIATE_CLUSTER_ENDPOINT,
                auth_credentials = weaviate.auth.AuthApiKey(self.WEVIATE_CLUSTER_API_KEY)
            )
        
        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def delete_weaviate_collection(
            self, 
            collection_name: str
        ):
        '''
        Delete a collection within Weaviate.
        '''
        try:
            LOGGER.info(f'Deleting collection: {collection_name}')
            with self.get_weaviate_client() as client:
                client.collections.delete(collection_name)
        
        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def get_weaviate_collection(
            self, 
            collection_name: str
        ):
        '''
        Delete a collection within Weaviate.
        '''
        try:
            LOGGER.info(f'Getting collection: {collection_name}')
            with self.get_weaviate_client() as client:
                return client.collections.get(collection_name)
        
        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def query_weaviate_collection(
            self, 
            collection_name: str,
            question_vector: str
        ):
        '''
        Delete a collection within Weaviate.
        '''
        try:
            LOGGER.info(f'Querying collection: {collection_name}')
            with self.get_weaviate_client() as client:
                collection = client.collections.get(collection_name)
                return collection.query.near_vector(
                    near_vector = question_vector,
                    limit = 1,
                )
        
        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def generate_embedding(
            self, 
            text: str
        ):
        '''
        Generate embeddings for an input string using embeddings API
        '''
        try:
            self._get_env_variables(variable_type='azure_openai')
            url = f"{self.AZURE_OPENAI_ENDPOINT}/openai/deployments/{self.AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME}/embeddings?api-version={self.AZURE_OPENAI_API_VERSION}"

            headers = {
                "Content-Type": "application/json",
                "api-key": self.AZURE_OPENAI_API_KEY,
            }
            data = {"input": text}
            response = requests.post(url, headers=headers, data=json.dumps(data)).json()

            embedding = response['data'][0]['embedding']

            LOGGER.info('Generated an embedding')
            return embedding

        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def count_tokens(
            self,
            text: str, 
            model_name: str  # ['text-embedding-ada-002', 'gpt-3.5-turbo']
        ) -> int:
        '''
        Computes the number of required tokens for an input text using tiktoken library.
        '''
        encoding = tiktoken.encoding_for_model(model_name)
        tokens = encoding.encode(text)
        return len(tokens)
    

    def count_words(
            self, 
            text: str,
        ) -> int:
        '''
        Counts the number of words in the input text.
        '''
        return len(text.split())
    

    def split_text_into_chunks(
            self,
            text: str,
            chunk_size: int = 500,
            chunk_overlap: int = 100
        ):
        '''
        Split a piece of text into chunks.
        '''
        text_splitter = TokenTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        text_splitted = text_splitter.split_text(text)
        return text_splitted


    def process_all_blobs_to_embeddings(
            self,
            table_names: list,
            collection_name: str,
            file_handler: FileHandler,
            database_handler: DatabaseHandler,
            blob_conversion_handler: BlobConversionHandler,
            truncate_db_table_embeddings: bool = False,
        ):
        '''
        Convert all textfiles from a SQL table to embeddings (word vectors), and save the result
        in SQL database (text + location) + Weaviate database (vector)
        '''
        # Clear output table if desired
        if truncate_db_table_embeddings:
            database_handler.truncate_table('Embeddings')

        data_filtered = []
        for table_name in table_names:
            query = f"SELECT * FROM {table_name}"
            data = database_handler.execute_query(query, fetch_results=True)
            data_filtered.extend([
                {
                    'Id': item['Id'], 
                    'LocationText': item['LocationText']
                } for item in data
            ])
        
        for blob_idx, blob_info in enumerate(data_filtered):
            LOGGER.info(f'> Blob [ {blob_idx + 1} / {data_filtered} ]')
            id = blob_info['Id']
            blob_name = blob_info['LocationText']

            arr_bytes = file_handler.get_blob_as_bytes(blob_name)
            text = blob_conversion_handler.get_text(blob_name, arr_bytes)
            chunks = self.split_text_into_chunks(text)

            for chunk_id, chunk_text in enumerate(chunks):
                embedding = self.generate_embedding(chunk_text)
                vector_id = uuid.uuid4()
                properties = {
                    'id_external': id,
                    'location_text': blob_name
                }

                # Upload embedding vector to weviate
                self.upload_to_weviate(
                    collection_name=collection_name,
                    properties=properties,
                    embedding=embedding,
                    vector_id=vector_id,
                )

                # Upload embedding text to sql databaee
                database_handler.upload_to_database_embeddings(
                    id=vector_id,
                    chunk_id=chunk_id,
                    chunk_text=chunk_text,
                    file_path_original_file=blob_name,
                )

    
    def upload_to_weviate(
            self,
            collection_name: str,
            properties: dict,
            embedding: list,
            vector_id: str = None,
        ):
        '''
        Upload a single object to a Weaviate collection.
        '''
        try:
            self._get_env_variables(variable_type='weaviate_cluster')
            vector_id = uuid.uuid4() if not vector_id else vector_id

            with weaviate.connect_to_wcs(
                cluster_url = self.WEVIATE_CLUSTER_ENDPOINT,
                auth_credentials = weaviate.auth.AuthApiKey(self.WEVIATE_CLUSTER_API_KEY)
            ) as client:
                collection_files = client.collections.get(collection_name)
                collection_files.data.insert(
                    properties=properties,
                    uuid=vector_id,
                    vector=embedding,
                )
            LOGGER.info(f'Uploaded single object to Weaviate collection {collection_name}')

        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def create_collection(
            self,
            name: str,
            properties: list,
            hard_reset: bool = False,
        ):
        try:
            self._get_env_variables(variable_type='weaviate_cluster')

            with self.get_weaviate_client() as client:
                # Delete a collection
                if hard_reset:
                    client.collections.delete(name)
                    LOGGER.info(f'Deleted Weaviate collection {name}') 
                # Create a collection
                client.collections.create(
                    name=name,
                    properties=properties,
                )
                LOGGER.info(f'Created Weaviate collection {name}')

        except Exception as e:
            LOGGER.error(f'Failed: {e}')

            