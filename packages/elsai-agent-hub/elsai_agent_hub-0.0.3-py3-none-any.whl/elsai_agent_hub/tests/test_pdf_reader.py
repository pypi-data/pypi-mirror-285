import pytest
from pathlib import Path, PurePath
from elsai_agent_hub.tools.read_document import ReadPdf


@pytest.fixture
def input_pdf_path():
    root_path = Path().root
    pdf_path = Path(str(PurePath(root_path, "source", "optisol-business-solution.pdf")))
    return str(pdf_path)


def test_return_type_in_pdf(input_pdf_path):
    # The function name should be start only as test_<function_name> same as folder name
    text = ReadPdf().pdf_reader(pdf_path=input_pdf_path)
    assert isinstance(text, str)


def test_len_in_pdf(input_pdf_path):
    text = ReadPdf().pdf_reader(pdf_path=input_pdf_path)
    assert len(text) == 1209


def test_content_in_pdf(input_pdf_path):
    text = ReadPdf().pdf_reader(pdf_path=input_pdf_path)
    assert "04/04/2024 OptiSol Business Solution Profile" in text


def test_specific_page_in_pdf(input_pdf_path):
    text = ReadPdf().pdf_reader(pdf_path=input_pdf_path, page_no=1)
    assert isinstance(text, str)
    assert len(text) == 907
    assert "04/04/2024 OptiSol Business Solution Profile" in text


def test_invalid_pdf_file_path():
    with pytest.raises(ValueError):
        ReadPdf().pdf_reader(pdf_path="")


def test_invalid_pdf_page_no(input_pdf_path):
    with pytest.raises(ValueError):
        ReadPdf().pdf_reader(pdf_path=input_pdf_path, page_no="first")
