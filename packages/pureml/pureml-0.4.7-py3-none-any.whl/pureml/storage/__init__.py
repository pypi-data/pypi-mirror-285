import platform
from pathlib import Path
from shutil import copyfileobj
from uuid import uuid4

import requests

from pureml.cli.helpers import get_auth_headers
from pureml.cli.puremlconfig import PureMLConfigYML
from pureml.components import get_org_id
from pureml.schema.backend import BackendSchema
from pureml.schema.request import AcceptHeader
from pureml.utils.logger import get_logger
from pureml.utils.routes import secrets_url

from .providers.aws import S3StorageProvider
from .providers.cloudflare import R2StorageProvider

project_path = Path.cwd()
if Path.exists(project_path / "puremlconfig.yaml"):
    puremlconfig = PureMLConfigYML(project_path / "puremlconfig.yaml")
else:
    puremlconfig = None

# backend_schema = BackendSchema().get_instance()
backend_schema = BackendSchema()

logger = get_logger("sdk.storage.__init__.py")


def upload_and_get_provider_and_path(
    file_path: str, storage_provider: str = None, opt_base_dir: str = ""
) -> str or None:
    """
    Gets the storage provider from config repository and uploads the file to the storage provider

    Config file should have the following format -
    repository: <storage_provider>://<repository_argument>

    repository_argument is the argument required for the storage provider
    for file : repository_argument is the path of the directory where the file is to be stored
    for s3 : repository_argument is the name of the secret made in pureml secrets for s3
    for r2 : repository_argument is the name of the secret made in pureml secrets for r2


    Parameters
    ----------
    file_path: str
        Path of the file to be uploaded

    storage_provider: str (default: None)
        Storage provider to be used for uploading the file

    Returns
    -------
    str, str or None
        Provider used and Path of the uploaded file or None if the file is not uploaded successfully
    """
    repository_argument = ""
    if storage_provider is None:
        if puremlconfig is not None:
            storage_provider = puremlconfig.data["repository"].split("://")[0]
            repository_argument = puremlconfig.data["repository"].split("://")[1]
        else:
            raise KeyError(
                "No storage provider found in config file. Please run `pureml init` to initialize the config file or update the `puremlconfig.yaml` config file manually"
            )

    if storage_provider not in ["s3", "r2", "file"]:
        raise ValueError(
            "Invalid storage provider. Currently supported storage providers are s3, r2 and file"
        )

    if storage_provider == "file":
        # if file storage is used, copy the file from given path to the repository_argument path
        # and return the path of the file
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError("File not found")
        if not Path(repository_argument).exists():
            # create the directory if it doesn't exist
            Path(repository_argument).mkdir(parents=True, exist_ok=True)
        file_path = file_path.resolve()

        # copy the file to the repository_argument path
        copyfileobj(
            file_path.open("rb"),
            (Path(repository_argument) / file_path.name).open("wb"),
        )

        # return the path of the file
        file_path = Path(repository_argument) / file_path.name
        return storage_provider, file_path.as_posix()

    system = platform.system()
    if system in ["Windows", "Linux", "Darwin"]:
        file_path = (
            file_path.replace(r"\\", "/").lstrip("/")
            if system == "Windows"
            else file_path.replace(r"\\", "/")
        )
    else:
        logger.error(
            f"Platform should be either windows, linux, darwin. Current Platform is {system}"
        )
        raise ("Platform should be either Windows, Linux, Darwin")

    # Get secrets from backend API
    get_org_id()
    url = secrets_url(repository_argument)

    headers = get_auth_headers(content_type=None, accept=AcceptHeader.APP_JSON)

    response = requests.get(url, headers=headers)
    #print(f"response __init__.py: {response}")
    if response.ok:
        secrets = response.json()["data"]
        if secrets and len(secrets) != 0:
            secrets = secrets[0]
    else:
        # print(response.json())
        raise ValueError("Invalid repository argument")

    # Get storage provider client
    keys_to_delete = [
        "source_type",
        "api_key",
        "organization_id",
        "deployment_name",
        "resource_name",
        "api_version",
    ]
    for key in keys_to_delete:
        if key in secrets:
            del secrets[key]
    storage_provider_client = get_storage_provider(storage_provider, **secrets)

    key = file_path.split("/")[-1]
    ext = key.split(".")[-1]
    name = ".".join(key.split(".")[:-1])
    random_string = str(uuid4())[:8]
    key = f"{opt_base_dir}/{name}_{random_string}.{ext}"
    upload_path = storage_provider_client.upload_file(file_path, key)
    print("upload_path", upload_path)

    if upload_path is None:
        raise ValueError("File not uploaded successfully")

    return storage_provider, upload_path


def get_storage_provider(provider, **kwargs):
    """
    Function to dynamically create a client for a storage provider
    NOTE: all keyword arguments are passed from backend secrets hence are defined in the providers although not used
    Currently supported storage providers -

    ---

    1. S3
    ...

    Required kwargs -

    access_key_id: str
        AWS access key

    access_key_secret: str
        AWS secret key

    bucket_name: str
        AWS bucket name

    bucket_location: str
        AWS region

    public_url: str (default: None)
        Public URL of the bucket

    2. R2
    ...

    Required kwargs -

    access_key_id: str
        Cloudflare access key

    access_key_secret: str
        Cloudflare secret key

    bucket_name: str
        Cloudflare bucket name

    account_id: str
        Cloudflare account ID

    public_url: str
        Public URL of the bucket
    """
    if provider == "s3":
        return S3StorageProvider(**kwargs)
    elif provider == "r2":
        return R2StorageProvider(**kwargs)
    # elif provider == "local":
    #     return LocalStorageProvider(**kwargs)
    else:
        raise ValueError("Invalid storage provider")
