import os
from .services.openai_service import OpenAIService
from .services.google_service import GoogleService
from .services.anthropic_service import AnthropicService

class AIManager:
    def __init__(self):
        self.services = {
            'openai': OpenAIService(api_key=os.getenv('OPENAI_API_KEY')),
            'google': GoogleService(api_key=os.getenv('GOOGLE_API_KEY')),
            'anthropic': AnthropicService(api_key=os.getenv('ANTHROPIC_API_KEY'))
        }
        print("API Keys Loaded:AIManager")
    
    def call_api(self, company, model, prompt):
        if company not in self.services:
            raise ValueError(f"Unsupported AI company: {company}")
        
        service = self.services[company]
        return service.generate_text(model, prompt)
