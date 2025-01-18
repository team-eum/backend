from openai import OpenAI
from openai.types.chat import ChatCompletion
from config.settings import OPENAI_API_KEY


class CustomOpenAI:

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def get_summary(self, text) -> ChatCompletion:
        return self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content":
                        f"""
                        Summarize this text in Korean.
                        {str(text)}
                        """
                }
            ]
        )


