import openai
import anthropic
from typing import List, Dict, Any, Optional
from app.config import settings, TECHPAL_SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        
        if settings.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    
    def _prepare_messages(self, conversation_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Prepare messages for LLM API calls"""
        messages = [{"role": "system", "content": TECHPAL_SYSTEM_PROMPT}]
        
        # Add conversation history
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return messages
    
    def _call_openai(self, messages: List[Dict[str, str]]) -> tuple[str, int]:
        """Call OpenAI API"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return content, tokens_used
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"Failed to get response from OpenAI: {str(e)}")
    
    def _call_anthropic(self, messages: List[Dict[str, str]]) -> tuple[str, int]:
        """Call Anthropic API"""
        try:
            # Convert messages to Anthropic format
            system_message = TECHPAL_SYSTEM_PROMPT
            user_messages = [msg["content"] for msg in messages if msg["role"] == "user"]
            assistant_messages = [msg["content"] for msg in messages if msg["role"] == "assistant"]
            
            # Create message list for Anthropic
            anthropic_messages = []
            for i in range(max(len(user_messages), len(assistant_messages))):
                if i < len(user_messages):
                    anthropic_messages.append({"role": "user", "content": user_messages[i]})
                if i < len(assistant_messages):
                    anthropic_messages.append({"role": "assistant", "content": assistant_messages[i]})
            
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.7,
                system=system_message,
                messages=anthropic_messages
            )
            
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            return content, tokens_used
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise Exception(f"Failed to get response from Anthropic: {str(e)}")
    
    def get_response(self, conversation_history: List[Dict[str, str]], provider: str = None) -> tuple[str, int, str]:
        """
        Get response from LLM provider
        
        Args:
            conversation_history: List of message dictionaries with 'role' and 'content'
            provider: 'openai' or 'anthropic'. If None, uses default from settings
            
        Returns:
            tuple: (response_content, tokens_used, provider_used)
        """
        if provider is None:
            provider = settings.default_llm_provider
        
        messages = self._prepare_messages(conversation_history)
        
        if provider == "openai":
            if not self.openai_client:
                raise Exception("OpenAI API key not configured")
            content, tokens = self._call_openai(messages)
        elif provider == "anthropic":
            if not self.anthropic_client:
                raise Exception("Anthropic API key not configured")
            content, tokens = self._call_anthropic(messages)
        else:
            raise Exception(f"Unsupported LLM provider: {provider}")
        
        return content, tokens, provider
    
    def validate_message(self, message: str) -> bool:
        """
        Basic validation to ensure message is appropriate for children
        
        Args:
            message: User message to validate
            
        Returns:
            bool: True if message is appropriate
        """
        # Convert to lowercase for checking
        message_lower = message.lower()
        
        # List of inappropriate words/phrases (basic filter)
        inappropriate_words = [
            "kill", "death", "suicide", "drugs", "alcohol", "sex", "porn",
            "hate", "racist", "terrorist", "bomb", "gun", "weapon"
        ]
        
        # Check for inappropriate content
        for word in inappropriate_words:
            if word in message_lower:
                return False
        
        # Check message length
        if len(message) > 1000:
            return False
        
        return True

# Global LLM service instance
llm_service = LLMService() 