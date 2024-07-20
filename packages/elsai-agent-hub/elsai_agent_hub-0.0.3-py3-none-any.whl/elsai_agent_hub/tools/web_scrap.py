from duckduckgo_search import DDGS, AsyncDDGS
from elsai_agent_hub.utils.log import setup_logger
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import BeautifulSoupTransformer


class WebScrap:
    def __init__(self) -> None:
        self.logger = setup_logger(__name__)

    def __search_sub_url(self, domain: str) -> list:
        """Domain name to extract the sub-urls

        Args:
            domain (str): Company domain URL

        Returns:
            list: List of URL's
        """
        try:
            self.logger.info("Crawling prospect details from domain name")
            count = 0
            results = [domain]
            while count < 3:
                try:
                    results = DDGS().text(domain, max_results=5)
                    break
                except:
                    count += 1
            if len(results) == 1:
                return results
            urls = [record["href"] for record in results if domain in record["href"]]
            return urls
        except Exception:
            return [domain]

    def read_url(self, domain: str = None, urls: list = []) -> str:
        """Reads the text from URL page

        Args:
            domain (str): A domain url to crawl and take multiple URL for webscraping . Defaults to None.
            urls(List): A List of urls to scrap the text from only given urls

        Raises:
            ValueError: Domain name can be string and not be empty

        Returns:
            str: Extracted text
        """
        if (not domain or not isinstance(domain, str)) and not urls:
            raise ValueError("Domain name can be string and not be empty")

        if not urls:
            urls = self.__search_sub_url(domain)
        loader = AsyncHtmlLoader(urls)
        docs = loader.load()

        bs_transformer = BeautifulSoupTransformer()
        docs_transformed = bs_transformer.transform_documents(
            docs, tags_to_extract=["span"]
        )

        text = ""
        for doc in docs_transformed:
            text = text + " " + doc.page_content
        return text
