import uuid
import chromadb
from pathlib import Path
from elsai_agent_hub.utils.utils import Utils
from langchain_text_splitters import RecursiveCharacterTextSplitter
from elsai_agent_hub.model.model import openai_embedding, azure_openai_embedding


class ChromaDB:
    def __init__(
        self,
        ai_service: str,
        collection_name: str = "default",
        persistent_path: str = None,
        azure_deployment_name: str = "text-embedding-3-small",
    ) -> None:
        """Initializes the ChromaDB instance with the specified AI service and collection name.

        Args:
            ai_service (str): The AI service to use ('azure' or 'openai').
            collection_name (str, optional): The name of the collection to create or retrieve. Defaults to 'default'.
            persistent_path (str, optional): The path for the persistent database. Defaults to None.
            azure_deployment_name (str, optional): The deployment name for the Azure service. Defaults to 'text-embedding-3-small'.
                                                   If the user selects Azure and provides a deployment name, it will be used. Otherwise, a default value will be used.

        Raises:
            ValueError: If the ai_service is not 'azure' or 'openai'.
        """
        if persistent_path and Path(persistent_path).exists():
            self.client = chromadb.PersistentClient(path=persistent_path)
        else:
            self.client = chromadb.Client()

        ai_service = ai_service.lower()
        if ai_service not in ["azure", "openai"]:
            raise ValueError("Please provide either azure or openai for LLM connection")

        if ai_service == "azure":
            self.openai_ef = azure_openai_embedding(model_name=azure_deployment_name)
        else:
            self.openai_ef = openai_embedding()

        self.collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=self.openai_ef
        )

    def store_data_into_db(
        self, document_directory: str, chunk_size: int = 6000, chunk_overlap: int = 20
    ):
        """Stores data into the vector database by splitting documents into chunks.

        Args:
            document_directory (str): The directory containing the documents to be processed.
            chunk_size (int, optional): The size of each text chunk. Defaults to 6000.
            chunk_overlap (int, optional): The overlap between text chunks. Defaults to 20.

        Raises:
            FileNotFoundError: If the document_directory is not a valid directory.
            RuntimeError: If unable to insert the data into the vector database.

        Returns:
            collection: The collection with the added documents.
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

            content = []
            ids = []
            for i, item in enumerate(documents):
                content.append(item)
                ids.append(str(uuid.uuid4()))

            self.collection.add(documents=content, ids=ids)
            return self.collection
        except Exception as exc:
            raise RuntimeError(
                "Unable to insert the data into the vector database"
            ) from exc

    def search_documents(self, query: str, number_of_doc: int = 5):
        """
        Searches for documents in the vector database based on the provided query.

        Args:
            query (str): The query text to search for.
            number_of_doc (int, optional): The number of documents to retrieve. Defaults to 5.

        Returns:
            response: The search response containing the relevant documents.

        Raises:
            RuntimeError: If unable to search the document from the database.
        """
        try:
            response = self.collection.query(
                query_texts=[query], n_results=number_of_doc
            )
            return response
        except Exception as exc:
            raise RuntimeError("Unable to search the document from database")
