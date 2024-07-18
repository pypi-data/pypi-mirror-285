import json
import requests

from .DatabaseHandler import DatabaseHandler
from .EmbeddingHandler import EmbeddingHandler
from .Printer import print_wrapped
from .Logger import Logger
from .DatabaseHandler import DatabaseHandler
from .Logger import Logger
from .Utils import Utils


LOGGER = Logger(
    name='ChatCompletor',
    log_to_console=True,
)

UTILS = Utils()


class ChatCompletor:
    def __init__(
            self,
        ) -> None:
        '''
        This class wil handle all Chat GPT completions related stuff.
        '''
        self.messages = []
        self.pre_prompt = ''
        self.retrieved_env_variables = False


    def _get_env_variables(
            self
        ):
        '''
        Get the necessary environment variables.
        '''
        if self.retrieved_env_variables:
            return
        
        self.AZURE_OPENAI_ENDPOINT = UTILS.get_env_variable('AZURE_OPENAI_ENDPOINT')
        self.AZURE_OPENAI_API_KEY = UTILS.get_env_variable('AZURE_OPENAI_API_KEY')
        self.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = UTILS.get_env_variable('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME')
        self.AZURE_OPENAI_API_VERSION = UTILS.get_env_variable('AZURE_OPENAI_API_VERSION')

        self.retrieved_env_variables = True


    def set_messages(
            self,
            messages: list,
        ):
        '''
        Set the history of the assistant, with given messages.
        '''
        try:
            LOGGER.info('Setting messages for assistant')
            self.messages = messages

        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def reset_assistant(
            self,
            pre_prompt: str,
        ):
        '''
        Reset the history of the assistant, with a fresh pre-prompt.
        '''
        try:
            LOGGER.info('Resetting assistant')
            self.pre_prompt = pre_prompt
            self.messages = [
                {
                    'role': 'system', 
                    'content': pre_prompt
                }
            ]

        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def append_messages(
            self, 
            role: str,
            content: str,
        ):
        '''
        Append new message to the history.
        '''
        LOGGER.info(f'{role}: {content}')
        self.messages.append({
            'role': role,
            'content': content
        })


    def chat_complete(
            self,
            question: str,
            answer: str = None,
            # messages: list = None,
        ):
        '''
        Return assistant chat response based on user query.
        Optional to give an answer which forces the assistant to reply using this answer.
        '''
        self._get_env_variables()
        try:
            LOGGER.info('Activating chat completion')
            if not self.messages:
                raise ValueError('No pre-prompt given. Run function ChatCompletor.reset_assistant() first.')

            messages_temp = []
            messages_temp.extend(self.messages)

            # Save question
            self.append_messages('user', question)

            if answer is not None:
                question = f'''De vraag is: {question}.\nGeef antwoord op basis van het volgende antwoord: {answer}'''

            messages_temp.append({
                'role': 'user',
                'content': question
            })

            # Create post request
            url = f"{self.AZURE_OPENAI_ENDPOINT}/openai/deployments/{self.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME}/chat/completions?api-version={self.AZURE_OPENAI_API_VERSION}"

            headers = {
                "Content-Type": "application/json",
                "api-key": self.AZURE_OPENAI_API_KEY
            }

            data = {
                "messages": messages_temp,
                # "temperature" : 0,
            }

            # LOGGER.info(f'MESSAGES_TEMP: {messages_temp}')

            response = requests.post(url, headers=headers, data=json.dumps(data)).json()

            # Save response message
            response_message = response['choices'][0]['message']
            # LOGGER.info(f'RESPONSE_MESSAGE: {response_message}')
            role = response_message['role']
            content = response_message['content']
            self.append_messages(role, content)

            return content
    
        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def answer_question_from_vector_database(
            self,
            question: str,
            collection_name: str,
            embedding_handler: EmbeddingHandler,
            database_handler: DatabaseHandler,
        ):
        '''
        Query a collection on Weaviate.
        '''
        try:
            LOGGER.info('Answering question using vector database')
            question_vector = embedding_handler.generate_embedding(question)
            # collection = embedding_handler.get_weaviate_collection(collection_name)
            # response = collection.query.near_vector(
            #     near_vector=question_vector,
            #     limit=1,
            # )
            response = embedding_handler.query_weaviate_collection(collection_name, question_vector)

            id_external = response.objects[0].uuid
            query = f"SELECT Text FROM Embeddings WHERE Id='{id_external}'"
            answer = database_handler.execute_query(query, fetch_results=True)[0]['Text']

            response_message = self.chat_complete(
                question=question,
                answer=answer,
            )

            return response_message
        
        except Exception as e:
            LOGGER.error(f'Failed: {e}')
    

    def print_conversation(
            self,
        ):
        '''
        Print the entire conversation
        '''
        print()
        for message in self.messages:
            role = message['role']
            content = message['content']
            print(f'> {role}')
            print('----------------------------')
            print_wrapped(content)
            print()