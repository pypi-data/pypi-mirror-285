from openai import APIConnectionError, APIError, OpenAI, RateLimitError

from ..provider import GatewayProvider


class OpenAIProvider(GatewayProvider):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.name = "OpenAI"
        self.client = OpenAI(api_key=api_key)
        self.chat.completions_create = self.chat_completions_create

    def validate_messages_policies(self, messages):
        # Validate messages policies here
        return True

    def chat_completions_create(self, model, messages, **kwargs):
        if not self.validate_messages_policies(messages):
            print("Messages validation failed")
            return None
        try:
            response = self.client.chat.completions.create(
                messages=messages, model=model, **kwargs
            )
        except APIConnectionError as e:
            # Handle connection error here
            print(f"Failed to connect to OpenAI API: {e}")
        except RateLimitError as e:
            # Handle rate limit error (we recommend using exponential backoff)
            print(f"OpenAI API request exceeded rate limit: {e}")
        except APIError as e:
            # Handle API error here, e.g. retry or log
            print(f"OpenAI API returned an API Error: {e}")
        return response
