from pathlib import Path

import typer
from pydantic import ConfigDict

from pureml.cli.puremlconfig import PureMLConfigYML

from .singleton import Singleton_BaseModel

project_path = Path.cwd()
if Path.exists(project_path / "puremlconfig.yaml"):
    puremlconfig = PureMLConfigYML(project_path / "puremlconfig.yaml")
else:
    puremlconfig = None


def get_backend_base_url(backend_url: str = None):
    if (
        backend_url is not None
        and backend_url != ""
        and type(backend_url) == typer.Option
    ):
        # override backend url (command specific option)
        return backend_url
    if puremlconfig is not None:
        # user configured backend url (self-hosted or custom pureml backend instance)
        backend_url = (
            puremlconfig.data["backend_url"]
            if "backend_url" in puremlconfig.data
            else "https://api.superalign.ai/api/v1/"
        )
    else:
        # default backend url (production cloud backend)
        backend_url = "https://api.superalign.ai/api/v1/"
    return backend_url


def get_frontend_base_url(frontend_url: str = None):
    if (
        frontend_url is not None
        and frontend_url != ""
        and type(frontend_url) == typer.Option
    ):
        # override frontend url (command specific option)
        return frontend_url
    if puremlconfig is not None:
        # user configured frontend url (self-hosted or custom pureml frontend instance)
        frontend_url = (
            puremlconfig.data["frontend_url"]
            if "frontend_url" in puremlconfig.data
            # else "https://pureml.com/"
            else "https://app.superalign.ai/"
        )
    else:
        # default frontend url (production cloud frontend)
        frontend_url = "https://app.superalign.ai/"
        # frontend_url = "https://pureml.com/"
    return frontend_url


class BackendSchema(Singleton_BaseModel):

    BASE_URL: str = get_backend_base_url()
    FRONTEND_BASE_URL: str = get_frontend_base_url()
    INTEGRATIONS: dict = {
        "s3": {
            "name": "AWS S3 Object Storage",
            "type": "storage",
            "secrets": [
                "access_key_id",
                "access_key_secret",
                "bucket_location",
                "bucket_name",
            ],
        },
        "r2": {
            "name": "Cloudflare R2 Object Storage",
            "type": "storage",
            "secrets": [
                "access_key_id",
                "access_key_secret",
                "account_id",
                "bucket_name",
                "public_url",
            ],
        },
        "openai": {
            "name": "OpenAI",
            "type": "model",
            "secrets": [
                "api_key",
            ],
            "optional_secrets": [
                "organization_id",
            ],
        },
        "azure-openai": {
            "name": "Azure OpenAI",
            "type": "model",
            "secrets": [
                "api_key",
                "deployment_name",
                "resource_name",
            ],
            "optional_secrets": [
                "api_version",
            ],
        },
    }
    model_config = ConfigDict(arbitrary_types_allowed=True)
