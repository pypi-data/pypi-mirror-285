# elsai-agent-hub: A multi-agent framework for GenAI

## Table of Contents

- [Introduction](#introduction)
- [Main Features](#main-features)
- [Installation](#installation)
- [License](#license)
- [Setup](#setup)
- [Usage](#usage)

## Introduction

**elsai-agent-hub** is a Python package designed to facilitate the quick and 
customized development of agent-driven applications leveraging large language 
models (LLMs). This library aims to streamline tasks such as content generation,
sending emails, and extracting information from various sources, including PDFs 
and web URLs.

## Main Features
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
  - **Document Vectorization**: Enable users to effortlessly vectorize documents
    (PDF, DOCX, TXT) from a given directory using ChromaDB or Pinecone for 
    efficient information retrieval. 
  - **Flexibility and Customization**: Highly customizable to suit specific 
    application requirements and workflows.

Whether you are looking to build a simple application or a complex system 
leveraging LLMs, **elsai-agent-hub** provides the fundamental building blocks 
to get you started quickly and efficiently.

## Directory Structure Diagram
   ![plot](source/ElsAI_Agent_Hub.png)

## Installation
You can install our package simply by running

    pip install elsai-agent-hub

## License
[MIT](LICENSE)

## Setup
### Environment Variables
    Depending on whether you are using Azure OpenAI or OpenAI, you need to set specific environment variables.

### Azure OpenAI
    If you are using Azure OpenAI, set the following environment variables:
    ```sh
    export AZURE_OPENAI_ENDPOINT=<Your_Endpoint>
    export AZURE_OPENAI_API_KEY=<Your_API_Key>
    export OPENAI_API_VERSION=<OpenAI_Version_Date>
    export AZURE_OPENAI_DEPLOYMENT_NAME=<Your_Deployment_Name>
    ```
### OpenAI
    If you are using OpenAI, set the following environment variable:
    ```sh
    export OPENAI_API_KEY=<Your_API_Key>
    ```

## Usage
   ### Content Generate
   It will analyze the query based on the given prompts
   
   #### Default prompt
    
   ##### For Azure

    ```python
    from elsai_agent_hub.micro_agent import ContentGenerate
    generated_text = ContentGenerate().generate(pdf_file_path='Your Pdf file-path',
                                                domain='Your Domain URL',
                                                text='your text',
                                                ai_service='azure')
    ```
   ##### For openAI

   ```python
   from elsai_agent_hub.micro_agent import ContentGenerate
   generated_text = ContentGenerate().generate(pdf_file_path='Your Pdf file-path',
                                              domain='Your Domain URL',
                                              text="your text",
                                              ai_service="openai")
   ```

   #### Custom Prompt

   ```python
   from elsai_agent_hub.micro_agent import ContentGenerate

   #Parameters
   """
   pdf_file_path (str): Path to a PDF file to be analyzed.
   ai_service (str): The AI service to use for analysis ('azure' or 'openai').
   urls (list, optional): A URL's to be extract and analyze. Defaults to an empty list. Defaults to None.
   text (str, optional): Text to be analyzed. Defaults to None.
   system_message (str, optional): A system message that may provide additional context for the analysis. Defaults to None.
   prompt (str, optional): A custom prompt for the AI service. If not provided, a default prompt will be used. Defaults to None.
   ai_config (dict, optional): Additional configuration parameters for the AI service. Defaults to an empty dictionary.
   """
   generated_text = ContentGenerate().generate(pdf_file_path='Your Pdf file-path',
                                              domain='Your Domain URL',
                                              text="your text",
                                              system_message="You are expert in data analysis"
                                              prompt="Analyze the document and provide tha valuable business insight"
                                              ai_service="openai") 
   ```

   ### Email Sender

   ```python
   from elsai_agent_hub.tools import EmailSender
   EmailSender().send_email(username="xxxx@gmail.com", #Login user mail ID
                         password="<Your APP Password>", #Corresponding APP password for login USER mail
                         sender_mail="xxxxx@gmail.com",
                         receiver_mail="yyyyy@gmail.com",
                         subject="Test Mail",
                         content_body="Howdy!")
   ```

   ### Sales Pitch Agent
   ```sh
    export LOGIN_MAIL='Your Gmail ID'
    export PASSWORD='Your 16 digit App password'
  ```
   ```python
   response = Sales().sales_pitch(pdf_file_path='Your Pdf file-path', #Product Details PDF file path
                csv_file_path='Your prospect CSV file', #Csv file path contains Name, Designation, Mail and Domain, 
                ai_service='azure',
                sender_name="Sender Name",
                sender_designation="Sender Designation",
                attachment='Attachment File path')
  ```

  ### Vectorization Using ChromaDB

  #### Using OpenAI
  ```python
  from elsai_agent_hub.micro_agent import ChromaDB
  chroma_db = ChromaDB(
    ai_service='openai',
    collection_name='your-collection-name',
    persistent_path='Your Database Storage Path'
  )
  collection = chroma_db.store_data_into_db(document_directory='Your Document Directory Path')
  response = chroma_db.search_documents("Your Query Text", number_of_doc=5)
  print(response)
  ```
  #### Using AzureOpenAI
   ```sh
    export AZURE_OPENAI_ENDPOINT=<Your_Endpoint>
    export AZURE_OPENAI_API_KEY=<Your_API_Key>
    export OPENAI_API_VERSION=<OpenAI_Version_Date>
    export AZURE_OPENAI_DEPLOYMENT_NAME='text-embedding-3-small'
  ```
  Note: Note: Make sure you create your deployment name as 'text-embedding-3-small' or any other embedding model pass ypu deployment-name as parameter while initialize.

  ```python
  from elsai_agent_hub.micro_agent import ChromaDB
  chroma_db = ChromaDB(
    ai_service='azure',
    collection_name='your-collection-name',
    persistent_path='Your Database Storage Path',
    azure_deployment_name='Deployment name for embedding model'
  )
  collection = chroma_db.store_data_into_db(document_directory='Your Document Directory Path')
  response = chroma_db.search_documents('Your Query Text', number_of_doc=5)
  print(response)
  ```

  ### Vectorization Using Pinecone

  #### Using OpenAI
  ```python
  from elsai_agent_hub.micro_agent import PineConeDB
  pinecone_db = PineConeDB('openai', index_name='Your Index Name')
  name_space = 'Your-Name-Space'
  index = pinecone_db.store_data_into_db(document_directory='Your Document Directory Path', name_space=name_space)
  response = pinecone_db.search_documents('Your Query Text', namespace=name_space)
  print(response)
  
  ```
  #### Using AzureOpenAI
  ```sh
    export AZURE_OPENAI_ENDPOINT=<Your_Endpoint>
    export AZURE_OPENAI_API_KEY=<Your_API_Key>
    export OPENAI_API_VERSION=<OpenAI_Version_Date>
    export AZURE_OPENAI_DEPLOYMENT_NAME=<deployment-name>
  ```
  Note: Make sure you create your deployment name as 'text-embedding-3-small' or any other embedding model pass ypu deployment-name as parameter while initialize.

  ```python
  from elsai_agent_hub.micro_agent import ChromaDB
  from elsai_agent_hub.micro_agent import PineConeDB
  pinecone_db = PineConeDB('azure', index_name='Your Index Name', azure_deployment_name='Deployment name for embedding model')
  name_space = 'Your-Name-Space'
  index = pinecone_db.store_data_into_db(document_directory='Your Document Directory Path', name_space=name_space)
  response = pinecone_db.search_documents('Your Query Text', namespace=name_space)
  print(response)
  ```