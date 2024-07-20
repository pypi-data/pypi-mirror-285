import pytest
from dotenv import load_dotenv
from pathlib import Path, PurePath
from elsai_agent_hub.micro_agent import ContentGenerate

load_dotenv()


@pytest.fixture
def input_pdf_path():
    root_path = Path().root
    pdf_path = Path(str(PurePath(root_path, "source", "optisol-business-solution.pdf")))
    return str(pdf_path)


@pytest.fixture
def input_web_scrap_urls():
    return [
        "https://www.optisolbusiness.com/about",
        "https://www.optisolbusiness.com/portfolio",
    ]


def test_analyze_document_azure(input_pdf_path):
    text = ContentGenerate().generate(pdf_file_path=input_pdf_path, ai_service="azure")
    assert isinstance(text, str)
    assert len(text) > 2


def test_analyze_document_openai(input_pdf_path):
    text = ContentGenerate().generate(pdf_file_path=input_pdf_path, ai_service="openai")
    assert isinstance(text, str)
    assert len(text) > 2


def test_analyze_urls_azure(input_web_scrap_urls):
    text = ContentGenerate().generate(urls=input_web_scrap_urls, ai_service="azure")
    assert isinstance(text, str)
    assert len(text) > 2


def test_analyze_urls_openai(input_web_scrap_urls):
    text = ContentGenerate().generate(urls=input_web_scrap_urls, ai_service="openai")
    assert isinstance(text, str)
    assert len(text) > 2
