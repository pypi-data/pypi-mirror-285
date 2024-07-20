import os
import chromadb.utils.embedding_functions as embedding_functions
from langchain_openai import (
    OpenAI,
    AzureChatOpenAI,
    OpenAIEmbeddings,
    AzureOpenAIEmbeddings,
)


def azure_openai():
    version = os.getenv("OPENAI_API_VERSION")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    if not version:
        raise ValueError("Environment variable 'OPENAI_API_VERSION' is not set.")
    if not endpoint:
        raise ValueError("Environment variable 'AZURE_OPENAI_ENDPOINT' is not set.")
    if not api_key:
        raise ValueError("Environment variable 'AZURE_OPENAI_API_KEY' is not set.")
    client = AzureChatOpenAI(
        api_key=api_key,
        api_version=version,
        azure_endpoint=endpoint,
        deployment_name=deployment_name,
    )
    return client


def openai():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Environment variable 'OPENAI_API_KEY' is not set.")
    client = OpenAI(openai_api_key=api_key)
    return client


def openai_embedding(model_name: str = "text-embedding-3-small"):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Environment variable 'OPENAI_API_KEY' is not set.")
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=api_key, model_name=model_name
    )
    return openai_ef


def azure_openai_embedding(model_name: str = "text-embedding-3-small"):
    version = os.getenv("OPENAI_API_VERSION")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    print(version, endpoint, api_key)
    if not version:
        raise ValueError("Environment variable 'OPENAI_API_VERSION' is not set.")
    if not endpoint:
        raise ValueError("Environment variable 'AZURE_OPENAI_ENDPOINT' is not set.")
    if not api_key:
        raise ValueError("Environment variable 'AZURE_OPENAI_API_KEY' is not set.")
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=api_key,
        api_base=endpoint,
        api_type="azure",
        api_version=version,
        model_name=model_name,
    )
    return openai_ef


def pinecone_openai_embedding(model: str = "text-embedding-3-small"):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Environment variable 'OPENAI_API_KEY' is not set.")
    embeddings = OpenAIEmbeddings(model=model)
    return embeddings


def pinecone_azure_openai_embedding(model_name: str = "text-embedding-3-small"):
    version = os.getenv("OPENAI_API_VERSION", "2024-02-01")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")

    if not version:
        raise ValueError("Environment variable 'OPENAI_API_VERSION' is not set.")
    if not endpoint:
        raise ValueError("Environment variable 'AZURE_OPENAI_ENDPOINT' is not set.")
    if not api_key:
        raise ValueError("Environment variable 'AZURE_OPENAI_API_KEY' is not set.")
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=model_name, openai_api_version=version
    )
    return embeddings
