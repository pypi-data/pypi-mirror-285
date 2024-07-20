import os
import uuid
from pathlib import Path
from pinecone import ServerlessSpec
from elsai_agent_hub.utils.utils import Utils
from pinecone.grpc import PineconeGRPC as Pinecone
from langchain_text_splitters import RecursiveCharacterTextSplitter
from elsai_agent_hub.model.model import (
    pinecone_openai_embedding,
    pinecone_azure_openai_embedding,
)


class PineConeDB:
    def __init__(
        self,
        ai_service: str,
        index_name: str = "default",
        dimension: int = 1536,
        metric: str = "cosine",
        cloud: str = "aws",
        region: str = "us-east-1",
        azure_deployment_name: str = "text-embedding-3-small",
    ) -> None:
        """Initialize the PineConeDB class.

        Args:
            ai_service (str): The AI service to use ('azure' or 'openai')
            index_name (str, optional): The name of the Pinecone index. Defaults to 'default'.
            dimension (int, optional): The dimension of the embeddings. Defaults to 1536.
            metric (str, optional): The similarity metric to use for the index. Defaults to 'cosine'.
            cloud (str, optional): The cloud provider for the Pinecone service. Defaults to 'aws'.
            region (str, optional): The region of the cloud provider. Defaults to 'us-east-1'.
            azure_deployment_name (str, optional): The deployment name for the Azure service. Defaults to 'text-embedding-3-small'.
                                                   If the user selects Azure and provides a deployment name, it will be used. Otherwise, a default value will be used.

        Raises:
            ValueError: If the 'PINECONE_API_KEY' environment variable is not set.
            ValueError: If the ai_service is not 'azure' or 'openai'.
        """
        pine_cone_api = os.getenv("PINECONE_API_KEY")
        if not pine_cone_api:
            raise ValueError("Environment variable 'PINECONE_API_KEY' is not set.")

        ai_service = ai_service.lower()
        if ai_service not in ["azure", "openai"]:
            raise ValueError("Please provide either azure or openai for LLM connection")

        if ai_service == "azure":
            self.embeddings = pinecone_azure_openai_embedding(
                model_name=azure_deployment_name
            )
        else:
            self.embeddings = pinecone_openai_embedding()

        self.pc = Pinecone(api_key=pine_cone_api)

        self.index_name = index_name

        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(cloud=cloud, region=region),
            )

    def store_data_into_db(
        self,
        document_directory: str,
        name_space: str = "doc",
        chunk_size: int = 6000,
        chunk_overlap: int = 20,
    ):
        """Store documents into the Pinecone database.

        Args:
            document_directory (str): The directory containing the documents to store.
            name_space (str, optional): The namespace for the documents. Defaults to 'doc'.
            chunk_size (int, optional): The size of each text chunk. Defaults to 6000.
            chunk_overlap (int, optional): The overlap between chunks. Defaults to 20.

        Raises:
            FileNotFoundError: If the document directory is not a valid path.
            RuntimeError: If unable to insert the data into the vector database.

        Returns:
            index: The Pinecone index with the stored data.
        """
        try:
            if not Path(document_directory).is_dir():
                raise FileNotFoundError("The directory path is not an valid path")

            text_content = Utils().reads_text_from_document_directory(
                document_directory
            )

            texts = "\n".join(text_content)

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                is_separator_regex=False,
            )

            documents = text_splitter.split_text(texts)

            pinecone_data = []
            for i, item in enumerate(documents):
                query_result = self.embeddings.embed_query(item)
                pinecone_data.append(
                    {
                        "id": str(uuid.uuid4()),
                        "values": query_result,
                        "metadata": {"text": item},
                    }
                )

            index = self.pc.Index(self.index_name)
            index.upsert(vectors=pinecone_data, namespace=name_space)
            return index
        except Exception as exc:
            raise RuntimeError(
                "Unable to insert the data into the vector database"
            ) from exc

    def search_documents(
        self,
        query: str,
        namespace: str = "doc",
        number_of_doc: int = 5,
        include_values: bool = True,
        include_metadata: bool = True,
    ):
        """Search for documents in the Pinecone database.

        Args:
            query (str): The query text to search for.
            namespace (str, optional): The namespace for the search. Defaults to 'doc'.
            number_of_doc (int, optional): The number of documents to retrieve. Defaults to 5.
            include_values (bool, optional):  Whether to include the values in the search results. Defaults to True.
            include_metadata (bool, optional):  Whether to include the metadata in the search results. Defaults to True.

        Raises:
            RuntimeError: If unable to search the documents in the database.

        Returns:
            _type_: The search results from the Pinecone database.
        """
        try:
            index = self.pc.Index(self.index_name)
            query_result = self.embeddings.embed_query(query)

            response = index.query(
                namespace=namespace,
                vector=query_result,
                top_k=number_of_doc,
                include_values=include_values,
                include_metadata=include_metadata,
            )

            return response
        except Exception as exc:
            raise RuntimeError("Unable to search the document from database")
