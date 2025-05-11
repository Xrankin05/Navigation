from openai import OpenAI
from openai._exceptions import OpenAIError
import os

# class Business(BaseModel):
#     name: str
#     address: str
#
# class Response(BaseModel):
#     business: Business

class AIAPI:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

    # Standard ChatGPT Interaction
    def getAPIResponse(self, path_text, model="gpt-4o-mini"):
        # This is where you direct the AI in it's response. (How are we going to get it from ChatGPT)
        system_message = "You are a helpful navigation assistant."

        # This is the same as the chatbox for ChatGPT. (What are we asking ChatGPT)
        user_message = f"""
        You are a navigation assistant. Given a list of grid path steps with row, col, and street name, generate step-by-step human-friendly directions like Google Maps.

        Use patterns like:
        - Continue down [street] for [X] blocks.
        - Turn left/right onto [street].
        - Arrive at destination.

        Here is the path:
        {path_text}
        """

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]

        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages
            )

            return completion.choices[0].message.content

        except OpenAIError as e:
        # Handle specific OpenAI errors
            print(f"OpenAI API error: {e}")
            return None
        except Exception as e:
            # Handle other potential errors
            print(f"An unexpected error occurred: {e}")
            return None

    # Custom Object ChatGPT Response
    # def getCustomAPIResponse(self, model = "gpt-4o-mini"):
    #     # This is where you direct the AI in it's response. (How are we going to get it from ChatGPT)
    #     system_message = ""
    #
    #     # This is the same as the chatbox for ChatGPT. (What are we asking ChatGPT)
    #     user_message = ""
    #
    #     messages = [
    #         {"role": "system", "content": system_message},
    #         {"role": "user", "content": user_message}
    #     ]
    #
    #     completion = self.client.chat.completions.create(
    #         model=model,
    #         messages=messages
    #     )
    #
    #     try:
    #         completion = self.client.beta.chat.completions.parse(
    #             model=model,
    #             messages=messages,
    #             response_format=Response
    #         )
    #
    #         responseMessage = completion.choices[0].message
    #         if responseMessage.parsed:
    #             return completion.choices[0].message.content
    #         else:
    #             print(f"Refused Response : \n{responseMessage.refusal}")
    #             return None
    #
    #     except OpenAIError as e:
    #         # Handle specific OpenAI errors
    #         print(f"OpenAI API error: {e}")
    #         return None
    #     except Exception as e:
    #         # Handle other potential errors
    #         print(f"An unexpected error occurred: {e}")
    #         return None
    #
    # def parse_custom_api_response(self, json_str: str) -> Response:
    #     try:
    #         # Load JSON string into a Python dictionary
    #         data = json.loads(json_str)
    #
    #         # Parse the dictionary into the ApiResponse model
    #         api_response = Response.model_validate(data)
    #         return api_response
    #     except ValidationError as e:
    #         print("Validation Error:", e)
    #         raise
