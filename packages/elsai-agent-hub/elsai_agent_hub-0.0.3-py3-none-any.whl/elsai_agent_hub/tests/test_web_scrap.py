import pytest
from elsai_agent_hub.tools.web_scrap import WebScrap


@pytest.fixture
def input_web_scrap_urls():
    return [
        "https://www.optisolbusiness.com/about",
        "https://www.optisolbusiness.com/portfolio",
    ]


@pytest.fixture
def input_web_scrap_single_url():
    return ["https://www.optisolbusiness.com/about"]


def test_web_scrap(input_web_scrap_urls):
    text = WebScrap().read_url(urls=input_web_scrap_urls)
    assert len(text) == 6353


def test_web_scrap_content(input_web_scrap_urls):
    text = WebScrap().read_url(urls=input_web_scrap_urls)
    assert "Joy through Gratitude!" in text


def test_web_scrap_single_url(input_web_scrap_single_url):
    text = WebScrap().read_url(urls=input_web_scrap_single_url)
    assert len(text) == 2564
    assert "Joy through Gratitude!" in text


def test_invalid_web_scrap_url(input_web_scrap_single_url):
    with pytest.raises(ValueError):
        WebScrap().read_url(input_web_scrap_urls)
