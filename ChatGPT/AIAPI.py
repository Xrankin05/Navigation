from openai import OpenAI
from openai._exceptions import OpenAIError
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
import os
import json

class Directions(BaseModel):
    start: str
    destination: str


class Response(BaseModel):
    dirs: Directions

class AIAPI:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

    def getAPIResponse(self, model = "gpt-4o-mini"):
        system_message = """
            This is where you direct the AI in it's response. (How are we going to get it from ChatGPT)
            """

        user_message = f"""
            This is the same as the chatbox for ChatGPT. (What are we trying to get from ChatGPT)
            """

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]

        try:
            completion = self.client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                response_format=Response
            )

            responseMessage = completion.choices[0].message
            if responseMessage.parsed:
                return completion.choices[0].message.content
            else:
                print(f"Refused Response : \n{responseMessage.refusal}")
                return None

        except OpenAIError as e:
            # Handle specific OpenAI errors
            print(f"OpenAI API error: {e}")
            return None
        except Exception as e:
            # Handle other potential errors
            print(f"An unexpected error occurred: {e}")
            return None

    def parse_api_response(self, json_str: str) -> Response:
        try:
            # Load JSON string into a Python dictionary
            data = json.loads(json_str)

            # Parse the dictionary into the ApiResponse model
            api_response = Response.model_validate(data)
            return api_response
        except ValidationError as e:
            print("Validation Error:", e)
            raise
