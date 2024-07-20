from elsai_agent_hub.tools import ReadPdf
from elsai_agent_hub.tools import WebScrap
from elsai_agent_hub.tools import EmailSender
from elsai_agent_hub.agent_workflow import SalesAgent
from elsai_agent_hub.micro_agent import ContentGenerate, ChromaDB, PineConeDB

__doc__ = """
elsai-agent-hub - An Agent-Driven Application Framework for LLM Applications
=============================================================================

**elsai-agent-hub** is a Python package designed to facilitate the quick and 
customized development of agent-driven applications leveraging large language 
models (LLMs). This library aims to streamline tasks such as content generation,
sending emails, and extracting information from various sources, including PDF 
files, DOCX files, TXT files,and web URLs.

Main Features
-------------
Here are some of the key features of elsai-agent-hub:

  - **Content Generation**: Create high-quality written content 
    tailored to specific needs and contexts using advanced LLMs.
  - **Sales Pitch Automation**: Automate the creation and sending of personalized
    sales pitch emails, improving outreach effectiveness and engagement rates
  - **PDF Text Extraction**: Seamless integration with PyMuPDF to read and 
    extract text from PDF files.
  - **Web Scraping**: Utilize BeautifulSoup to scrape and extract data from 
    web URLs.
  - **Email Automation**: Send emails securely using SMTP with best practices 
    incorporated.
  - **Document Vectorization**: Vectorize documents (PDF, DOCX, TXT) from a 
    given directory using ChromaDB or Pinecone for efficient information retrieval.
  - **Flexibility and Customization**: Highly customizable to suit specific 
    application requirements and workflows.

Whether you are looking to build a simple application or a complex system 
leveraging LLMs, **elsai-agent-hub** provides the fundamental building blocks 
to get you started quickly and efficiently.

"""

__all__ = [
    "ReadPdf",
    "ChromaDB",
    "WebScrap",
    "PineConeDB",
    "SalesAgent",
    "EmailSender",
    "ContentGenerate",
]
