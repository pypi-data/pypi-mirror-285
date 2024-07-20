from openai import AzureOpenAI

from ..provider import GatewayProvider


class AzureOpenAIProvider(GatewayProvider):
    def __init__(self, api_key, api_version, endpoint):
        super().__init__(api_key, api_version, endpoint)
        self.name = "Azure OpenAI"
        self.client = AzureOpenAI(
            api_key=api_key, api_version=api_version, endpoint=endpoint
        )
        self.chat.completions_create = self.completions_create

    def validate_messages_policies(self, messages):
        # Validate messages policies here
        return True

    def chat_completions_create(self, model, messages, **kwargs):
        if not self.validate_messages_policies(messages):
            print("Messages validation failed")
            return None
        try:
            response = self.client.completions.create(
                messages=messages, model=model, **kwargs
            )
        except Exception as e:
            # Handle error here
            print(f"Failed to connect to Azure OpenAI API: {e}")
        return response
