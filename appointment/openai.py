from openai import OpenAI
from openai.types.chat import ChatCompletion
from config.settings import OPENAI_API_KEY


class CustomOpenAI:

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    def get_prompt(self, text):
        return f"""
        Summarize the provided transcript in Korean, focusing solely on the answers given by the mentor. 
        Emphasize the most important and frequently mentioned points.

        # Steps
        
        1. Read the entire transcript to understand the context and content.
        2. Identify the answers provided by the mentor.
        3. Extract key points from the mentor's responses that are important or frequently mentioned.
        4. Summarize these points while ensuring the summary is concise and accurately reflects the mentor's contributions.
        
        # Output Format
        
        - The summary should be in Korean.
        - Write in paragraph format, focusing on clarity and conciseness.
        ```markdown
        # 요약
        - **중요 내용 1** :
        - **중요 내용 2** :
        중요 내용이 더 있다면 계속 추가
        ```
        
        # Notes
        
        - Prioritize information in the mentor's responses that repeats or is emphasized in the transcript.
        - Ensure all translations to Korean maintain the original meaning and context.
        - Please provide a summary of the following topic in Markdown format:

        # Transcript given by mentor
        {text}
        """

    def get_summary(self, text) -> str:
        prompt: str = self.get_prompt(text)
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response.choices[0].message.content.replace("```markdown", "").replace("```", "").strip()
