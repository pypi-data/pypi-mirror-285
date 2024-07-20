import os
import anthropic

class AnthropicService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.default_max_tokens = int(os.getenv('MAX_TOKENS', 1000))

    def generate_text(self, model, prompt, max_tokens=None):
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens or self.default_max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return self.process_response(response)
        except Exception as e:
            raise Exception(f"Error in generating text: {str(e)}")

    def process_response(self, response):
        if response.content:
            return {
                'choices': [{
                    'message': {
                        'content': response.content[0].text
                    }
                }]
            }
        else:
            raise Exception('No valid content found in response')