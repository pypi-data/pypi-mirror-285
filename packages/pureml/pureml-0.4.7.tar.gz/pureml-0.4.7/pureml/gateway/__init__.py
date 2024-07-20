import json
from urllib.parse import urljoin

import requests

from pureml.cli.helpers import get_auth_headers, save_auth
from pureml.components import get_org_id
from pureml.schema.backend import BackendSchema
from pureml.schema.request import AcceptHeader
from pureml.utils.logger import get_logger

from .provider import GatewayProvider

backend_schema = BackendSchema()
logger = get_logger(name="sdk.gateway")


class Gateway:
    def __init__(self, name, secret_name, pureml_api_key=None):
        if pureml_api_key is not None:
            save_auth(api_token=pureml_api_key)
        self.gateway_name = name
        self.pureml_api_key = pureml_api_key
        self.secret_name = secret_name
        self.secret_details = self.get_secret(secret_name)
        self.supported_providers = ["azure-openai", "openai"]
        self.gateway_provider = self.get_gateway_provider()
        self.chat = Chat(self.gateway_name, self.gateway_provider)
        logger.info(f"Gateway initialized with provider: {self.gateway_provider.name}")

    def get_secret(self, secret_name: str) -> dict:
        # Implement logic to fetch the secret value from a secure store
        # using the provided `secret_name`
        if secret_name == "":
            raise ValueError("Secret name cannot be empty")

        # Get secrets from backend API
        get_org_id()
        url = f"secrets/{str(secret_name)}"
        url = urljoin(backend_schema.BASE_URL, url)
        # print(url)

        headers = get_auth_headers(content_type=None, accept=AcceptHeader.APP_JSON)

        response = requests.get(url, headers=headers)

        if response.ok:
            secrets = response.json()["data"]
            if secrets and len(secrets) != 0:
                secrets = secrets[0]
        else:
            # print(response.json())
            logger.error(f"Failed to fetch secrets: {response.json()}")
            raise ValueError("Invalid repository argument")

        # Get storage provider client
        secret_details = dict(secrets)
        logger.info(f"Secrets fetched successfully")
        return secret_details

    def get_gateway_provider(self) -> GatewayProvider:
        # Implement logic to determine the GatewayProvider based on the `secret_details`
        if not "source_type" in self.secret_details.keys():
            raise ValueError("Provider not found in secret details")
        provider = str(self.secret_details["source_type"]).lower()
        if provider not in self.supported_providers:
            raise ValueError(f"Provider {provider} not supported")
        if provider == "openai":
            from .providers.openai import OpenAIProvider

            required_keys = set(["api_key"])
            if not required_keys.issubset(self.secret_details.keys()):
                logger.error("Required keys not found in secret details")
                raise ValueError("Required keys not found in secret details")
            return OpenAIProvider(self.secret_details["api_key"])
        elif provider == "azure-openai":
            from .providers.azure_openai import AzureOpenAIProvider

            required_keys = set(["api_key", "api_version", "endpoint"])
            if not required_keys.issubset(self.secret_details.keys()):
                logger.error("Required keys not found in secret details")
                raise ValueError("Required keys not found in secret details")
            return AzureOpenAIProvider(
                self.secret_details["api_key"],
                self.secret_details["api_version"],
                self.secret_details["endpoint"],
            )
        else:
            raise NotImplementedError(f"Provider {provider} not implemented")


class ChatMessage:
    content: str
    role: str
    name: str = ""


class Chat:
    def __init__(self, gateway_name: str, gateway_provider: GatewayProvider):
        self.gateway_name = gateway_name
        self.gateway_provider = gateway_provider

    async def completions_create(self, model: str, messages: list[ChatMessage]):
        response = self.gateway_provider.chat.completions_create(model, messages)
        if len(response.choices) == 0:
            raise ValueError("No response choices received from provider")
        responseChoiceText = response.choices[0].message.content
        logger.info(f"Response successfully received from provider")
        # Log response to backend
        get_org_id()
        url = f"llm/logs"
        url = urljoin(backend_schema.BASE_URL, url)
        headers = get_auth_headers(content_type=None, accept=AcceptHeader.APP_JSON)
        data = {
            "provider": self.gateway_provider.name.lower(),
            "model": model,
            "name": self.gateway_name,
            "prompt": json.dumps(messages),
            "response": responseChoiceText,
        }
        apiresponse = requests.post(url, headers=headers, json=data)
        if apiresponse.ok:
            logger.info("Response logged successfully")
        else:
            logger.error(f"Error logging response: {apiresponse.__dict__}")
        return response
