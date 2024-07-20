import traceback
import pandas as pd
from pathlib import Path
from .log import setup_logger
from elsai_agent_hub.tools import WebScrap
from elsai_agent_hub.tools import ReadPdf, DocxPath, TxtPath


class Utils:
    def __init__(self) -> None:
        self.logger = setup_logger(__name__)

    def extract_text(
        self,
        pdf_file_path: str = None,
        url: str = None,
        urls: list = [],
        text: str = None,
    ) -> str:
        """Extracts the text from source

        Args:
            pdf_file_path (str, optional): Path to a PDF file to be analyzed. Defaults to None.
            urls (list, optional): A list of URLs whose content is to be analyzed. Defaults to an empty list.
            text (str, optional): Text to be analyzed. Defaults to None.

        Returns:
            str : Extracted text
        """
        prompt_text = ""
        if pdf_file_path:
            temp_text = ReadPdf().pdf_reader(pdf_file_path)
            prompt_text += temp_text
        if url:
            temp_text = WebScrap().read_url(url)
            prompt_text = prompt_text + " " + temp_text
        if urls:
            temp_text = WebScrap().read_url(urls=urls)
            prompt_text = prompt_text + " " + temp_text
        if text:
            prompt_text = prompt_text + " " + text
        return prompt_text

    def read_csv(self, csv_file_path: str):
        df = pd.read_csv(csv_file_path)
        return df

    def extract_text_from_files(self, file_path: Path):
        try:
            file_extension = file_path.suffix.lower()
            if file_extension == ".pdf":
                return ReadPdf().pdf_reader(file_path)
            elif file_extension == ".docx":
                return DocxPath().docx_reader(file_path)
            elif file_extension == ".txt":
                return TxtPath().txt_reader(file_path)
            else:
                return ""
        except Exception:
            print(traceback.format_exc())
            self.logger.error(rf"Unable to extract the file {str(file_path)}")
            return ""

    def reads_text_from_document_directory(self, directory_path: str):
        try:
            text_content = []
            for file in Path(directory_path).iterdir():
                if file.is_file():
                    text = self.extract_text_from_files(file)
                    if text:
                        text_content.append(text)
            return text_content
        except Exception:
            raise RuntimeError("Unable to extract the text from document")
