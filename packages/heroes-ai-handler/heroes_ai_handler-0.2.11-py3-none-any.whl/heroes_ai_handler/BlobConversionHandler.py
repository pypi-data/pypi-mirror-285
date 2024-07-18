import os
from langdetect import detect
from docx import Document
from io import BytesIO
import requests
import pymupdf

from .Logger import Logger
from .Utils import Utils


LOGGER = Logger(
    name='BlobConversionHandler',
    log_to_console=True,
)

UTILS = Utils()


class BlobConversionHandler:
    
    def __init__(
            self,
            translate: bool = True, 
            target_language: str = 'en',
        ) -> None:
        self.translate = translate
        self.target_language = target_language


    def get_text(
            self, 
            file_path: str,
            arr_bytes: bytes
        ):
        '''
        Get the text of the file in a string.
        '''
        LOGGER.info(f'Processing file: {file_path}')
        extension = os.path.splitext(file_path)[-1]
        self.file_path = file_path

        text = ''
        if extension == '.txt':
            text = self.convert_txt(arr_bytes)
        elif extension == '.pdf':
            text = self.convert_pdf(arr_bytes)
        elif extension == '.docx':
            text = self.convert_docx(arr_bytes)
        
        if text.strip() == '':
            return text

        if self.translate:
            text = self.detect_and_translate_libre(text)
        
        return text


    def detect_and_translate_libre(
            self, 
            text: str
        ):
        '''
        Detect the language of a piece of text and translate to the target lan
        '''
        try:
            # Detect the language of the input text
            LOGGER.info(f'Detecting language')
            detected_language = detect(text)

            if detected_language == self.target_language:
                return text
            
            LOGGER.info(f'Translating to: {self.target_language}')
            
            # Define the LibreTranslate API endpoint
            url = "https://libretranslate.com/translate"

            # Set up the parameters for the API request
            params = {
                "q": text,
                "source": detected_language,
                "target": self.target_language,
                "format": "text"
            }

            # Make the API request
            response = requests.post(url, data=params)

            # Check if the request was successful
            if response.status_code == 200:
                translation = response.json()["translatedText"]
                return translation
            else:
                raise Exception(f"Error: {response.status_code} - {response.text}")
        
        except Exception as e:
            LOGGER.error(f'Failed: {e}')
    
    
    def convert_txt(
            self, 
            arr_bytes: bytes
        ):
        '''
        Convert .txt documents to string.
        '''
        try:
            LOGGER.info('Converting text file to text')
            text = arr_bytes.decode('utf-8')
            return text

        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def convert_docx(
            self,
            arr_bytes: bytes
        ):
        '''
        Convert .docx documents to string.
        '''
        try:
            LOGGER.info('Converting Word document to text')
            doc = Document(BytesIO(arr_bytes))
            text = '\n'.join([para.text for para in doc.paragraphs])
            return text
    
        except Exception as e:
            LOGGER.error(f'Failed: {e}')
        
    def convert_pdf(
            self,
            arr_bytes: bytes
        ):
        '''
        Convert .pdf documents to string.
        '''
        try:
            LOGGER.info('Converting PDF document to text')
            pdf_document = pymupdf.open(stream=arr_bytes, filetype="pdf")
            text = ""
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            return text
        
        except Exception as e:
            LOGGER.error(f'Failed: {e}')