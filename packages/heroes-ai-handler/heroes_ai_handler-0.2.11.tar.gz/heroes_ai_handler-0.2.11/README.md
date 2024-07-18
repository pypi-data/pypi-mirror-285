python version >=  3.10
# Heroes AI Handler

## Description

This package will handle all elements for an AI assistant, from ingesting data to using the GPT models.

## Development
```bash
python3.10 -m venv .venv
pip install -r requirements.txt
```


## Usage of the package
For using this package, a few environment variables are necessary to use certain functionalities of the package. For example, place them all in a `.env` file, and load them in using package `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()
```

Full list of necessary variables:

Varibale name | description
|:--|:--|
AZURE_OPENAI_ENDPOINT | Endpoint to the Azure Open AI resource.
AZURE_OPENAI_API_KEY | API-key to access the Azure Open AI resource.
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME | Name of the deployment of the chat completion model.
AZURE_OPENAI_API_VERSION | API-versie azure Open AI resource.
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME | Name of the deployment of the embedding model.
WEVIATE_CLUSTER_ENDPOINT | Endpoint to the Weaviate cluster.
WEVIATE_CLUSTER_API_KEY | API-key to access the Weaviate cluster.
STORAGE_ACCOUNT_NAME | Name of the Azure Storage Account.
STORAGE_ACCOUNT_KEY | Key to the Azure Storage Account
STORAGE_ACCOUNT_CONTAINER_NAME | Container name within the Azure Storage Account
SQL_SERVER_NAME | SQL Server name.
SQL_DATABASE_NAME | Database name within SQL Server.
SQL_USERNAME | Username for accessing Database.
SQL_PASSWORD | Password for accessing Database.
SQL_DRIVER | Formulate SQL driver.


## Manual actions

Create the following resources:

**Azure**
- Azure OpenAI
    - Deploy chat completion model: gpt-3.5-turbo / gpt4
    - Deploy text embedding model: text-embedding-ada-002
- Storage account
    - Create container
- SQL server
    - Make sure you can access the SQL Server from the network configurations.
- SQL database
    - To create tables in database, run:
    `setup/1__create_database_tables.ipynb`

**Weaviate**
- Weaviate account with a cluster
    - To create collection in Weaviate cluster, run: 
    `setup/2__create_weaviate_collection.ipynb`



## Manual deployment of package

Only run this when automatical deployment through azure devops doesn't suit the purpose.

```bash
python3.10 -m venv .venv_publish
source .venv_publish/bin/activate
pip install wheel twine
rm -rf build dist *.egg-info
python setup.py sdist bdist_wheel
twine upload -u $(twineUsername) -p $(twinePassword) dist/*
rm -rf build dist *.egg-info
```
