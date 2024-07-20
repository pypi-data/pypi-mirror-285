class GatewayProvider:
    def __init__(self, api_key, api_version=None, endpoint=None):
        self.name = "Not defined"
        self.api_key = api_key
        self.api_version = api_version
        self.endpoint = endpoint
        self.client = None
        self.chat = Chat(self)

    def validate_messages_policies(self, messages) -> bool:
        raise NotImplementedError(
            "validate_prompt_policies method must be implemented by the provider"
        )


class Chat:
    def __init__(self, provider: GatewayProvider):
        self.provider = provider

    def completions_create(self, model: str, messages, **kwargs):
        raise NotImplementedError(
            "completions_create method must be implemented by the provider"
        )
