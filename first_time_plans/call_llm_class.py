from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import Type, List, Dict
from pydantic import BaseModel
import openai

# Load environment variables and set up the API client
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)
OPENAI_MODEL = "gpt-4o-mini"


class SimpleLLMClient:
    """
    SYSTEM: A simple LLM client that wraps around OpenAI's API.
    Chain of Thought:
      - Initialize with an API key.
      - Use the OpenAI library to send a prompt.
      - Return the LLM response as a string.
    """
    
    def __init__(self):
        self.api_key = client
        self.model = OPENAI_MODEL


    def analyze(self, prompt: str) -> str:
        """
        SYSTEM: Sends the prompt to the LLM and returns the analysis.
        Chain of Thought:
          - Create a conversation with a system message and user prompt.
          - Call the OpenAI ChatCompletion API.
          - Return the content of the assistant's reply.
        """
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides detailed analysis based on given prompts."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content']
    
    def analyze_two_json(self, prompt: str, system_message:  str, response_format: Type[BaseModel]):
        
        completion = client.beta.chat.completions.parse(
        model=self.model,
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        response_format=response_format,
        )

        response_json =  completion.choices[0].message.parsed

        return response_json        

        
        


