from openai import OpenAI, Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk


class CustomOpenAI:

    def __init__(self):
        self.client = OpenAI()

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


