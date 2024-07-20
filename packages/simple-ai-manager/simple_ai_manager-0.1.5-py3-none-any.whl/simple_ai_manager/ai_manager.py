import os
from .services.openai_service import OpenAIService
from .services.google_service import GoogleService
from .services.anthropic_service import AnthropicService

class AIManager:
    def __init__(self, default_save_conversation=False):
        self.services = {
            'openai': OpenAIService(api_key=os.getenv('OPENAI_API_KEY')),
            'google': GoogleService(api_key=os.getenv('GOOGLE_API_KEY')),
            'anthropic': AnthropicService(api_key=os.getenv('ANTHROPIC_API_KEY'))
        }
        self.conversations = {}
        self.default_save_conversation = default_save_conversation

    def start_conversation(self, company, model, save_conversation=None):
        if company not in self.services:
            raise ValueError(f"Unsupported AI company: {company}")
        
        if save_conversation is None:
            save_conversation = self.default_save_conversation

        conversation_id = f"{company}_{model}_{len(self.conversations)}"
        if save_conversation:
            self.conversations[conversation_id] = {'company': company, 'model': model, 'history': []}
        return conversation_id

    def call_api(self, company, model, prompt, conversation_id=None):
        if company not in self.services:
            raise ValueError(f"Unsupported AI company: {company}")
        
        service = self.services[company]
        
        if conversation_id and conversation_id in self.conversations:
            conversation = self.conversations[conversation_id]
            response = service.continue_conversation(model, prompt, conversation['history'])
            conversation['history'].append({'role': 'user', 'content': prompt})
            conversation['history'].append({'role': 'assistant', 'content': response})
        else:
            response = service.generate_text(model, prompt)
        
        return response

    def end_conversation(self, conversation_id):
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]