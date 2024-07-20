import pytest
from pathlib import Path, PurePath
from elsai_agent_hub.micro_agent.vector_db import PineConeDB


@pytest.fixture
def input_dir_path():
    root_path = Path().root
    document_directory = Path(str(PurePath(root_path, "source")))
    return str(document_directory)


def test_pinecone_db(input_dir_path):
    pinecone_db = PineConeDB("openai", index_name="something")
    name_space = "Sri"
    index = pinecone_db.store_data_into_db(
        document_directory=input_dir_path, name_space=name_space
    )
    response = pinecone_db.search_documents(
        "Limited Control over Source Selection", namespace=name_space
    )
    assert True
