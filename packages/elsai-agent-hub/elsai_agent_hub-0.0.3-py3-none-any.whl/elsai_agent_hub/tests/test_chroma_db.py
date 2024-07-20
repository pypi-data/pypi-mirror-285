import pytest
from pathlib import Path, PurePath
from elsai_agent_hub.micro_agent.vector_db import ChromaDB


@pytest.fixture
def input_dir_path():
    root_path = Path().root
    document_directory = Path(str(PurePath(root_path, "source")))
    return str(document_directory)


def test_chroma_db(input_dir_path):
    chroma_db = ChromaDB(ai_service="openai", collection_name="sri")
    collection = chroma_db.store_data_into_db(document_directory=input_dir_path)
    response = chroma_db.search_documents(
        "Something",
        number_of_doc=10,
    )
    assert len(response) == 8
    assert isinstance(response, dict)
