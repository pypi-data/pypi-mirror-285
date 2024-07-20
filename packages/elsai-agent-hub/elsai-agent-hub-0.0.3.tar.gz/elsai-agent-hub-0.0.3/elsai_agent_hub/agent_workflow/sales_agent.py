import os
from pathlib import Path
from elsai_agent_hub.utils.utils import Utils
from langchain_core.prompts import PromptTemplate
from elsai_agent_hub.utils.log import setup_logger
from elsai_agent_hub.tools.read_document import ReadPdf
from elsai_agent_hub.tools.web_scrap import WebScrap
from elsai_agent_hub.tools.email_sender import EmailSender
from langchain_core.output_parsers import JsonOutputParser
from elsai_agent_hub.model.model import azure_openai, openai


class SalesAgent:
    def __init__(self) -> None:
        self.sender = os.getenv("SENDER_EMAIL")
        self.login = os.getenv("LOGIN_MAIL")
        self.password = os.getenv("PASSWORD")
        self.logger = setup_logger(__name__)

    def __invoke_model(
        self,
        pdf_file_path: str,
        domain: str,
        prompt: str,
        recipient_name: str,
        recipient_designation: str,
        sender_name: str,
        sender_designation: str,
        ai_service: str,
    ) -> bool:
        self.logger.info(rf"Preparing mail content for {recipient_name}")
        try:
            if ai_service == "azure":
                llm = azure_openai()
            else:
                llm = openai()

            product_text = ReadPdf().pdf_reader(pdf_file_path)
            prospect_details = WebScrap().read_url(domain=domain)

            template = prompt

            prompt_template = PromptTemplate.from_template(template)

            parser = JsonOutputParser()

            llm_chain = prompt_template | llm | parser

            llm_response = llm_chain.invoke(
                {
                    "product_details": product_text,
                    "company_details": prospect_details,
                    "recipient_name": recipient_name,
                    "recipient_designation": recipient_designation,
                    "sender_name": sender_name,
                    "sender_designation": sender_designation,
                }
            )

            return llm_response
        except Exception as exc:
            raise RuntimeError("Unable to generate response from LLM") from exc

    def sales_pitch(
        self,
        pdf_file_path: str,
        csv_file_path: str,
        ai_service: str,
        system_message: str = None,
        prompt: str = None,
        sender_name: str = "",
        sender_designation: str = "unspecified",
        attachment: str = None,
    ) -> str:
        """Analyze the product and prospect details and send the sales pitch to the prospect.

        Args:
            pdf_file_path (str): Path to a PDF file to be analyze the product details. Defaults to None.
            csv_file_path (str): Path to the CSV file regarding the prospect details. Defaults to None.
            ai_service (str): The AI service to use for analysis ('azure' or 'openai'). Defaults to None.
            system_message (str, optional): A system message that may provide additional context for the analysis. Defaults to None.
            prompt (str, optional): A custom prompt for the AI service. If not provided, a default prompt will be used. Defaults to None.
            sender_name (str, optional): Sender name to mentioned for regards. Defaults to "".
            sender_designation (str, optional): Sender designation to mentioned for regards. Defaults to "".
            attachment (str, optional): If any attachment file to be attached. Defaults to None.

        Raises:
            ValueError: If the PDF file is provided as empty path
            ValueError: If the CSV file path is empty
            ValueError: If ai_service is not 'azure' or 'openai'.
            ValueError: If there are required missing columns in the CSV
            RuntimeError: If error occurred while executing the function

        Returns:
            str: The response message
        """
        try:
            if not pdf_file_path:
                raise ValueError("please provide the product details in PDF file")

            if not csv_file_path:
                raise ValueError(
                    "Please provide the recipient details in the CSV file, In the column name of Name,Mail,Designation,Domain"
                )

            if not Path(pdf_file_path).exists():
                raise ValueError(
                    rf"The file {pdf_file_path} does not exist in the given path."
                )

            if not Path(csv_file_path).exists():
                raise ValueError(
                    rf"The file {csv_file_path} does not exist in the given path."
                )

            ai_service = ai_service.lower()
            if ai_service not in ["azure", "openai"]:
                raise ValueError(
                    "Please provide either azure or openai for LLM connection"
                )

            if not system_message:
                system_message = "You are an expert AI sales assistant with a deep understanding of marketing and sales strategies. Your role is to analyze the provided product details and compose a professional, persuasive sales pitch email."

            if not prompt:
                prompt = """You are an AI assistant tasked with generating personalized sales pitch emails. Below, you'll find detailed information about a product and a prospect company. Your goal is to craft an engaging and persuasive email that highlights the key features and benefits of the product, tailored to the prospect company's specific needs and context. The email should be customized based on the recipient's designation (technical, business, unspecified).

                        Product Details:
                        {product_details}

                        Prospect Company Details:
                        {company_details}

                        Recipient Information:

                        Recipient Name: {recipient_name}
                        Recipient Designation: {recipient_designation}
                        Sender Information:

                        Sender Name: {sender_name}
                        Sender Designation: {sender_designation}
                        Task:

                        Generate a personalized sales pitch email using the provided information. Ensure the email is professional, engaging, and clearly communicates how the product can address the specific needs of the prospect company. Use the recipient's name in the greeting and the sender's name and designation in the closing. Tailor the email content based on the recipient's designation as follows:

                        Technical (e.g., CTO, Chief Data Officer): Focus on technical features, performance, and integration capabilities.
                        Business (e.g., CEO, CFO): Highlight business benefits, ROI, and strategic advantages.
                        Unspecified: Provide a balanced overview of both technical features and business benefits.
                        Output:
                        Provide the generated email with the subject and body as JSON keys. Ensure the email content is realistic, removing any placeholder text like "[company detail]" and replacing it with appropriate content.
                        """

            df = Utils().read_csv(csv_file_path)
            required_columns = ["Name", "Mail", "Domain"]
            missing_columns = [
                field for field in required_columns if field not in df.columns
            ]
            if missing_columns:
                raise ValueError(
                    f"Missing required columns in the CSV: {', '.join(missing_columns)}"
                )

            for index, row in df.iterrows():
                name = row["Name"]
                mail = row["Mail"]
                domain = row["Domain"]

                print(name, mail, domain)
                if "Designation" in row:
                    designation = row["Designation"]
                else:
                    designation = "CEO"

                llm_response = self.__invoke_model(
                    pdf_file_path,
                    domain,
                    prompt,
                    name,
                    designation,
                    sender_name,
                    sender_designation,
                    ai_service,
                )

                if llm_response:
                    self.logger.info(rf"Sending mail content to {name}")
                    EmailSender().send_email(
                        self.login,
                        self.password,
                        self.sender,
                        mail,
                        llm_response["subject"],
                        llm_response["body"],
                        attachment,
                    )
                    self.logger.info(rf"Mail sent to {name}")
                    df.loc[index, "Mail Status"] = "Sent"
                else:
                    self.logger.error(rf"Unable to send the mail to {name}")
                    df.loc[index, "Mail Status"] = "Not Sent"
            df.to_csv(csv_file_path, index=False)
            return {
                "status": "Updated the status in same CSV under the column name of 'Mail Status'"
            }
        except Exception as exc:
            self.logger.error("Error occurred in pitching the sales mail")
            raise RuntimeError("Unable to send an email to client's") from exc
