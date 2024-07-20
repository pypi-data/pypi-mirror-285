import os
import google.generativeai as genai

class GoogleService:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.default_max_tokens = int(os.getenv('MAX_TOKENS', 8192))
        self.generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": self.default_max_tokens,
        }

    def generate_text(self, model_name, prompt, max_tokens=None):
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=self.generation_config
        )
        
        if max_tokens:
            model.generation_config["max_output_tokens"] = max_tokens
        
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error in generating text: {str(e)}")