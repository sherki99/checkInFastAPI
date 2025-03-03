import os
import json
from typing import Any, Dict, Optional, Type
from dotenv import load_dotenv
from pydantic import BaseModel
import openai
from openai import OpenAI
import time

# Load environment variables and set up the API client
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)
OPENAI_MODEL = "gpt-4o-mini"


class BaseLLM:
    """
    Super class for interacting with the LLM.

    Supports:
      - Function calling for action-driven responses.
      - Structured outputs to enforce a JSON schema.
      - Standard text responses.
    """
    def __init__(self, llm_client: Optional[Any] = None, model: str = OPENAI_MODEL):
        self.llm_client = llm_client or client
        self.model = model
        self.system_message = "You are a helpful assistant."
    
    def call_llm(
        self,
        prompt: str,
        system_message:  str,
        schema: Optional[Type[BaseModel]] = None,
        function_schema: Optional[Dict] = None
    ) -> Any:
        """
        Call the LLM with the provided prompt.
        
        :param prompt: The user's message.
        :param schema: A Pydantic model class defining the JSON schema for structured outputs.
        :param function_schema: A dictionary defining a function's schema for function calling.
        :return: The response from the LLM, parsed as JSON or plain text.
        """

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        
        # Case 1: Use function calling if a function schema is provided
        if function_schema:
            tools = [{
                "type": "function",
                "function": function_schema
            }]
            max_retries = 5
            wait_time = 1  # initial wait time in seconds

            for attempt in range(max_retries):
                try:
                    completion = self.llm_client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=tools
                    )
                    # Expect at least one function call in the response
                    tool_call = completion.choices[0].message.tool_calls[0]
                    return json.loads(tool_call.function.arguments)
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"Attempt {attempt+1} failed, waiting {wait_time} seconds before retrying...")
                        time.sleep(wait_time)
                        wait_time *= 2  # Increase wait time exponentially
                    else:
                        raise e
        # Case 2: Use structured JSON outputs if a Pydantic schema is provided
        elif schema:
            completion = self.llm_client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=schema
            )
            return json.loads(completion.choices[0].message.content)
        
        # Case 3: Otherwise, return the plain text response
        else:
            completion = self.llm_client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return completion.choices[0].message.content
