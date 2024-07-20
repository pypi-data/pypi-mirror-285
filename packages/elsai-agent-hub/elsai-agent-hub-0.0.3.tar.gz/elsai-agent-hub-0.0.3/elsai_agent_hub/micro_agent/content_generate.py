from elsai_agent_hub.utils.utils import Utils
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from elsai_agent_hub.model.model import azure_openai, openai


class ContentGenerate:

    def generate(
        self,
        pdf_file_path: str,
        ai_service: str,
        urls: str = [],
        text: str = None,
        system_message: str = None,
        prompt: str = None,
        ai_config: dict = {},
    ) -> str:
        """
        Generate the content based on the provided input and prompt.

         Args:
             pdf_file_path (str): Path to a PDF file to be analyzed. Defaults to None.
             ai_service (str): The AI service to use for analysis ('azure' or 'openai'). Defaults to None.
             urls (list, optional): A URL's to be extract and analyze. Defaults to an empty list.
             text (str, optional): Text to be analyzed. Defaults to None.
             system_message (str, optional): A system message that may provide additional context for the analysis. Defaults to None.
             prompt (str, optional): A custom prompt for the AI service. If not provided, a default prompt will be used. Defaults to None.
             ai_config (dict, optional): Additional configuration parameters for the AI service. Defaults to an empty dictionary.

         Raises:
             ValueError: If none of pdf_file_path, urls, or text is provided.
             ValueError: If ai_service is not 'azure' or 'openai'.
             RuntimeError: If error occurred while executing the function"

         Returns:
             str: The generated results.
        """
        try:
            if not pdf_file_path and not urls and not text:
                raise ValueError(
                    "please provide atleast any one pdf_file_path, urls or text"
                )

            if not system_message:
                system_message = "You are a highly intelligent and knowledgeable business consultant with expertise in various domains including finance, marketing, operations, and strategy. Your goal is to analyze the provided text and offer insightful, actionable steps for the business. You will identify key areas that need improvement, highlight any missing elements, and suggest corrections or enhancements. Your responses should be clear, concise, and actionable, aimed at driving the business forward."

            if not prompt:
                prompt = """You are an expert blog writer. Your task is to create a compelling and informative blog post using the content provided below. The blog post should include a catchy title, an engaging introduction, well-organized body sections with clear headings, and a thought-provoking conclusion. Each section should flow naturally and maintain reader interest. Ensure the use of proper grammar, varied sentence structure, and a tone appropriate for the topic.

                            Instructions:

                            Title: Craft a catchy and relevant title that captures the essence of the blog post.
                            Introduction: Provide an engaging introduction that introduces the main topic, explains its significance, and sets the stage for the rest of the post.
                            Body Sections: Divide the content into logical sections with clear and informative headings. Each section should delve into specific aspects of the topic, providing detailed explanations, examples, and any relevant data or statistics.
                            Conclusion: Summarize the key points discussed in the body sections, offer final thoughts, and include a call to action or a thought-provoking statement to leave a lasting impression on the reader.
                        """

            ai_service = ai_service.lower()
            if ai_service not in ["azure", "openai"]:
                raise ValueError(
                    "Please provide either azure or openai for LLM connection"
                )

            if ai_service == "azure":
                llm = azure_openai()
            else:
                llm = openai()

            prompt_text = Utils().extract_text(
                pdf_file_path=pdf_file_path, urls=urls, text=text
            )

            template = """Content: {prompt_text} 
                            
            Prompt: """
            template = template + prompt

            prompt_template = PromptTemplate.from_template(template)

            output_parser = StrOutputParser()

            llm_chain = prompt_template | llm | output_parser

            llm_response = llm_chain.invoke(prompt_text)

            return llm_response
        except Exception as exc:
            raise RuntimeError("Unable to analyze the text") from exc
