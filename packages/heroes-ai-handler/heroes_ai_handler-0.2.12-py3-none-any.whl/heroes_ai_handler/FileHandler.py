
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import hashlib

from .Logger import Logger
from .BlobConversionHandler import BlobConversionHandler
from .DatabaseHandler import DatabaseHandler
from .Utils import Utils


LOGGER = Logger(
    name='FileHandler',
    log_to_console=True,
)

UTILS = Utils()


class FileHandler():
    def __init__(
            self,
        ) -> None:
        '''
        This class will handle all file related stuff for local files, or a connected blob storage with a given container.
        '''
        self.retrieved_env_variables = False
        self.blob_service_client = self._get_blob_service_client()
        self.container_client = self._get_container_client()


    def _get_env_variables(
            self
        ):
        '''
        Get the necessary environment variables.
        '''
        if self.retrieved_env_variables:
            return
        
        self.STORAGE_ACCOUNT_NAME = UTILS.get_env_variable('STORAGE_ACCOUNT_NAME')
        self.STORAGE_ACCOUNT_KEY = UTILS.get_env_variable('STORAGE_ACCOUNT_KEY')
        self.STORAGE_ACCOUNT_CONTAINER_NAME = UTILS.get_env_variable('STORAGE_ACCOUNT_CONTAINER_NAME')

        self.retrieved_env_variables = True


    def _get_blob_service_client(
            self,
            storage_account_name: str = None,
            storage_account_key: str = None,
        ) -> BlobServiceClient:
        '''
        Get a Blob Service Client.
        '''
        try:
            self._get_env_variables()
            if not storage_account_name:
                storage_account_name = self.STORAGE_ACCOUNT_NAME
            if not storage_account_key:
                storage_account_key = self.STORAGE_ACCOUNT_KEY
            LOGGER.info(f'Getting a Blob Service Client for storage account: {storage_account_name}')
            blob_service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net", credential=storage_account_key)
            return blob_service_client
        
        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def _get_container_client(
            self,
            container_name: str = None,
        ) -> ContainerClient:
        '''
        Get a Container Client.
        '''
        try:
            if not container_name:
                container_name = self.STORAGE_ACCOUNT_CONTAINER_NAME
            LOGGER.info('Getting a Container Client ...')
            container_client = self.blob_service_client.get_container_client(container=container_name)
            return container_client
        
        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def _get_blob_client(
            self,
            blob_name: str,
        ) -> BlobClient:
        '''
        Get a Blob Client.
        '''
        try:
            LOGGER.info(f'Getting a Blob Client for blob: {blob_name}')
            blob_client = self.container_client.get_blob_client(blob=blob_name)
            return blob_client
        
        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def get_blob_as_bytes(
            self,
            blob_name: str,
        ) -> BlobClient:
        '''
        Get a blob as bytes.
        '''
        try:
            LOGGER.info(f'Downloading a blob as bytes: {blob_name}')
            return self._get_blob_client(blob_name).download_blob().readall()

        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def list_files_in_local_folder(
            self,
            folder_path: str,
        ):
        '''
        List all files in a local folder.
        '''
        file_paths = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_paths.append(os.path.join(root, file))
        return file_paths


    def load_urls_from_local_file(
            self,
            file_path: str,
        ):
        '''
        Open the file and read all lines.
        '''
        with open(file_path, 'r') as file:
            lines_raw = file.readlines()

        lines = []
        for line in lines_raw:
            line = line.strip()
            if line == '':
                continue
            lines.append(line)
        return lines


    def upload_file_to_blob(
            self,
            file_path_src: str, 
            file_path_dst: str,
        ):
        '''
        Upload a local file to blob storage.
        '''
        try:
            # Create a blob client using the local file name as the name for the blob
            blob_client = self._get_blob_client(file_path_dst)

            # Upload the created file
            LOGGER.info(f'Uploading: [{file_path_src}] to blob location: [{file_path_dst}]')
            with open(file_path_src, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)

        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def list_blobs_in_folder(
            self,
            folder_path: str,
            sort_blobs: bool = True,
            only_files: bool = False
        ):
        '''
        List all blobs in blob storage folder.
        '''
        blobs_list = []
        # Ensure the folder path ends with a '/' for proper filtering
        if not folder_path.endswith('/'):
            folder_path += '/'

        blobs = self.container_client.list_blobs(name_starts_with=folder_path)
        for blob in blobs:
            blobs_list.append(blob.name)

        # Sort list of blobs based upon length.
        if sort_blobs:
            blobs_list = sorted(blobs_list, key=len)[::-1]

        if only_files:
            # Only select files
            blobs_list_temp = []
            for blob_name in blobs_list:
                _, file_extension = os.path.splitext(blob_name)
                if file_extension != '':
                    blobs_list_temp.append(blob_name)
            blobs_list = blobs_list_temp

        return blobs_list


    def delete_blobs_in_folder(
            self, 
            folder_path: str,
        ):
        '''
        Delete all blobs in a blob storage folder.
        '''
        # Ensure the folder path ends with a '/' for proper filtering
        if not folder_path.endswith('/'):
            folder_path += '/'

        # List all blobs
        blob_names = self.list_blobs_in_folder(folder_path, only_files=False)

        # Delete each blob individually
        for blob_name in blob_names:
            try:
                LOGGER.info(f'Deleting blob: {blob_name}')
                blob_client = self._get_blob_client(blob_name)
                blob_client.delete_blob()

            except Exception as e:
                LOGGER.error(f'Failed: {e}')


    def copy_local_files_to_blob(
            self,
            dir_src: str,
            dir_dst: str,
            delete_all_blobs_first: bool = True
        ):
        '''
        Copy files from local folder to blob storage.
        '''
        # Delete all blobs in destination folder first
        if delete_all_blobs_first:
            self.delete_blobs_in_folder(dir_dst)

        # Find all files to copy
        file_paths_src = self.list_files_in_local_folder(dir_src)

        # Copy all files to blob container folder
        for file_path_src in file_paths_src:
            file_path_dst = os.path.join(dir_dst, file_path_src[len(dir_src) + 1:])
            self.upload_file_to_blob(file_path_src, file_path_dst)


    def download_blob_files_to_local(
            self,
            dir_src: str,
            dir_dst: str,
            delete_files_in_dir_dst: bool = True
        ):
        '''
        Download all blobs from the container, but only if they are files.
        '''
        # Delete all files in destination folder
        if delete_files_in_dir_dst:
            self.delete_all_files_in_local_folder(dir_dst)

        # Ensure the folder path ends with a '/' for proper filtering
        if not dir_src.endswith('/'):
            dir_src += '/'

        # List all blobs
        blob_names = self.list_blobs_in_folder(
            folder_path='raw/files_original',
            sort_blobs=True,
            only_files=True
        )

        # Download each blob individually
        for blob_name in blob_names:
            # file_path_dst = os.path.join(dir_dst, blob_name[len(dir_src):])
            file_path_dst = os.path.join(dir_dst, os.path.relpath(blob_name, dir_src))
            self.download_blob(blob_name, file_path_dst)


    def download_blob(
            self,
            blob_name: str,
            file_path_dst: str,
        ):
        '''
        Download a single blob to local folder
        '''
        # Ensure the directory for the blob exists
        os.makedirs(os.path.dirname(file_path_dst), exist_ok=True)

        try:
            LOGGER.info(f'Downloading blob: {blob_name}')
            with open(file_path_dst, "wb") as download_file:
                download_file.write(self.get_blob_as_bytes(blob_name))

        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def delete_all_files_in_local_folder(
            self,
            folder_path: str,
        ):
        '''
        Delete all files in local folder.
        '''
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    LOGGER.info(f'Deleting local file: {file_path}')
                    os.remove(file_path)

                except Exception as e:
                    LOGGER.error(f"Failed: {e}")

            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    LOGGER.info(f'Deleting local file: {file_path}')
                    os.rmdir(dir_path)

                except OSError as e:
                    # The directory is not empty
                    LOGGER.error(f"Failed: {e}")


    def generate_id(
            self,
            value: str,
        ):
        '''
        Generate an unique id based upon a given string value.
        '''
        return hashlib.sha1(value.encode('utf-8')).hexdigest()


    def process_multiple_blobs(
            self,
            dir_src: str,
            dir_dst: str,
            blob_conversion_handler: BlobConversionHandler,
            database_handler: DatabaseHandler,
            clear_output_folder: bool = False,
            truncate_database_table: bool = False,
        ):
        # Clear output folder if desired
        if clear_output_folder:
            self.delete_blobs_in_folder(dir_dst)

        # Clear output table if desired
        if truncate_database_table:
            database_handler.truncate_table('Files')

        # List all blobs in source folder
        blob_names = self.list_blobs_in_folder(dir_src, only_files=True)
        for blob_name in blob_names:
            self.process_individual_blob(blob_name, dir_dst, blob_conversion_handler, database_handler)


    def process_individual_blob(
            self,
            blob_name: str,
            dir_dst: str,
            blob_conversion_handler: BlobConversionHandler,
            database_handler: DatabaseHandler,
        ):
        try:
            LOGGER.info(f'Processing blob: {blob_name}')
            
            file_name_full = os.path.basename(blob_name)
            file_name, file_extension = os.path.splitext(file_name_full)
            arr_bytes = self.get_blob_as_bytes(blob_name)
            text = blob_conversion_handler.get_text(blob_name, arr_bytes)

            # Generate output location
            id = self.generate_id(blob_name)
            file_path_dst = os.path.join(dir_dst, id + '.txt')

            # Upload to blob storage
            self.upload_to_blob_storage(file_path_dst, text)

            # Upload to Database
            database_handler.upload_to_database_files(id, blob_name, file_extension, file_path_dst)
        
        except Exception as e:
            LOGGER.error(f'Failed: {e}')


    def upload_to_blob_storage(
            self,
            file_path_dst: str,
            text: str,
        ):
        '''
        Upload some text directly to a given blob storage location.
        '''
        if file_path_dst is None:
            return
        
        try:
            LOGGER.info(f'Saving blob to: {file_path_dst}')
            destination_blob_client: BlobClient = self._get_blob_client(file_path_dst)
            destination_blob_client.upload_blob(text, overwrite=True)

        except Exception as e:
            LOGGER.error(f'Failed: {e}')