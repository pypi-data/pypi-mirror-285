import openai
import os

class OpenAIService:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key
        self.default_max_tokens = int(os.getenv('MAX_TOKENS', 1000))

    def generate_text(self, model, prompt, max_tokens=None):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens or self.default_max_tokens
            )
            return self.process_response(response)
        except Exception as e:
            raise Exception(f"Error in generating text: {str(e)}")

    def process_response(self, response):
        if response.choices and response.choices[0].message:
            return {
                'choices': [{
                    'message': {
                        'content': response.choices[0].message.content
                    }
                }]
            }
        else:
            raise Exception('No valid content found in response')