import os
from openai import OpenAI


class ConfigOpenAI:
    """
    Initializes environment and gets api key
    """

    def __init__(self):
        self.open_ai_api_key = os.getenv("OPENAI_API_KEY")


class Client(ConfigOpenAI):
    """
    Assistant Client
    ----------------
    Initializes client object for making API requests.

    Passes Open AI API key to the API endpoint, initializing the client for use.
    """

    def __init__(self):
        super().__init__()  # Parent ConfigOpenAI class contains the API key processing
        self.client = OpenAI(api_key=self.open_ai_api_key)


if __name__ == "__main__":
    Client()
