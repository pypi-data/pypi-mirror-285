from urllib.parse import urljoin

import requests
import typer
from rich import print
from rich.console import Console
from rich.table import Table

from pureml.cli.helpers import get_auth_headers
from pureml.components import get_org_id
from pureml.schema.request import ContentTypeHeader
from pureml.schema.backend import get_backend_base_url, BackendSchema
from pureml.schema.paths import PathSchema
from pureml.utils.logger import get_logger

path_schema = PathSchema()
backend_schema = BackendSchema()
app = typer.Typer()
logger = get_logger(name="sdk.cli.secrets")


@app.callback()
def callback():
    """
    Manage organization secrets

    Use with add, show, delete option

    add - Adds new secret for any integration
    all - Gets all secret names for the organization
    show - Show all secrets of secret name
    delete - Delete secrets under secret name
    """


@app.command()
def add(
    backend_url: str = typer.Option(
        "",
        "--backend-url",
        "-b",
        help="Backend URL for self-hosted or custom pureml backend instance",
    )
):
    """
    Add a new integration and it's secrets

    Usage:
    pureml secrets add
    """
    logger.info("Add new integration and secrets")
    backend_base_url = get_backend_base_url(backend_url)

    # Show all integrations
    print()
    console = Console()
    table = Table("Sr.No.", "Integration Name", "Integration type")
    sr_no = 1
    for integration in backend_schema.INTEGRATIONS:
        integration_data = backend_schema.INTEGRATIONS[integration]
        table.add_row(
            str(sr_no), integration_data["name"], integration_data["type"]
        )
        sr_no += 1
    console.print(table)
    print()

    # Get integration id
    sr_no = -1
    count = len(backend_schema.INTEGRATIONS.keys())
    while int(sr_no) not in range(1, count + 1):
        sr_no: str = typer.prompt(
            "Enter the Sr.No. of Integration you want to use (1 .... "
            + str(count)
            + ")"
        )
        if int(sr_no) not in range(1, count + 1):
            print("[red]Invalid Sr.No. of Integration![/red]")
    integration_id = list(backend_schema.INTEGRATIONS.keys())[int(sr_no) - 1]

    # Get secret name
    secret_name: str = ""
    while not secret_name:
        secret_name = typer.prompt(
            "Enter a unique secret name for this integration"
        )

    # Get secret keys and values according to integration
    secret_keys = backend_schema.INTEGRATIONS[integration_id]["secrets"]
    user_secrets = {}
    for secret_key in secret_keys:
        secret_value = ""
        while not secret_value:
            secret_value = typer.prompt(f"Enter the value for {secret_key}")
        user_secrets[secret_key] = secret_value

    # Get optional secret keys and values according to integration
    if "optional_secrets" in backend_schema.INTEGRATIONS[integration_id]:
        optional_secret_keys = backend_schema.INTEGRATIONS[integration_id][
            "optional_secrets"
        ]
        user_optional_secrets = {}
        for secret_key in optional_secret_keys:
            secret_value = typer.prompt(
                f"Enter the value for {secret_key} [optional]", default=""
            )
            user_optional_secrets[secret_key] = secret_value

    # Add secret
    get_org_id()

    data = {}
    url_path = ""

    # match integration_id:
    if integration_id == "s3":
        # case "s3":
        data = {
            "access_key_id": user_secrets["access_key_id"],
            "access_key_secret": user_secrets["access_key_secret"],
            "bucket_location": user_secrets["bucket_location"],
            "bucket_name": user_secrets["bucket_name"],
            "secret_name": secret_name,
            "storage_type": "s3",
        }
        url_path = "secrets/storages"
    elif integration_id == "r2":
        # case "r2":
        data = {
            "access_key_id": user_secrets["access_key_id"],
            "access_key_secret": user_secrets["access_key_secret"],
            "account_id": user_secrets["account_id"],
            "bucket_name": user_secrets["bucket_name"],
            "public_url": user_secrets["public_url"],
            "secret_name": secret_name,
            "storage_type": "r2",
        }
        url_path = "secrets/storages"
    elif integration_id == "openai":
        # case "openai":
        data = {
            "api_key": user_secrets["api_key"],
            "secret_name": secret_name,
            "organization_id": user_optional_secrets.get("organization_id", ""),
            "provider_type": "openai",
        }
        url_path = "secrets/providers"
    elif integration_id == "azure-openai":
        # case "azure-openai":
        data = {
            "api_key": user_secrets["api_key"],
            "deployment_name": user_secrets["deployment_name"],
            "resource_name": user_secrets["resource_name"],
            "api_version": user_optional_secrets.get(
                "api_version", "2024-02-01"
            ),
            "secret_name": secret_name,
            "provider_type": "azure-openai",
        }
        url_path = "secrets/providers"

    url = urljoin(backend_base_url, url_path)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_JSON)

    response = requests.post(url, json=data, headers=headers)
    if response.ok:
        print(f"[green]Successfully added secrets for {secret_name}[/green]")

    else:
        logger.error("Unable to add integration!", response=response)
        print("[red]Unable to fetch secrets!")


@app.command()
def all(
    backend_url: str = typer.Option(
        "",
        "--backend-url",
        "-b",
        help="Backend URL for self-hosted or custom pureml backend instance",
    )
):
    """
    Get all secret names for the organization

    Usage:
    pureml secrets all
    """
    logger.info("Get all secrets for the organization")
    backend_base_url = get_backend_base_url(backend_url)

    print()
    get_org_id()
    url_path = "secrets"
    url = urljoin(backend_base_url, url_path)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_JSON)

    response = requests.get(url, headers=headers)

    if response.ok:
        secrets_all = response.json()["data"]
        if not secrets_all or len(secrets_all) == 0:
            print("[red]No secrets found[/red]")
            return
        console = Console()

        table = Table("Secret Name")
        for secret in secrets_all:
            table.add_row(secret)

        console.print(table)
        print()
    else:
        logger.error("Unable to fetch secrets!", response=response)
        print("[red]Unable to fetch secrets!")


@app.command()
def show(
    secret_name: str = typer.Argument(..., case_sensitive=True),
    backend_url: str = typer.Option(
        "",
        "--backend-url",
        "-b",
        help="Backend URL for self-hosted or custom pureml backend instance",
    ),
):
    """
    Shows the secrets under given secret name

    Usage:
    pureml secrets show "secret_name"
    """
    logger.info(f"Show secrets for {secret_name}")
    backend_base_url = get_backend_base_url(backend_url)

    print()
    get_org_id()
    url_path = f"secrets/{secret_name}"
    url = urljoin(backend_base_url, url_path)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_JSON)

    response = requests.get(url, headers=headers)

    if response.ok:
        secrets_all = response.json()["data"]
        if not secrets_all or len(secrets_all) == 0:
            print(f"[red]No secrets found for {secret_name}[/red]")
            return
        secrets_all = secrets_all[0]

        print()
        print(f"[green]{secret_name} secrets :")
        console = Console()

        table = Table("Key", "Value")
        for key, value in secrets_all.items():
            if value != "":
                table.add_row(key, value)

        console.print(table)
        print()

    else:
        logger.error("Unable to fetch secrets!", response=response)
        print("[red]Unable to fetch secrets!")


@app.command()
def delete(
    secret_name: str = typer.Argument(..., case_sensitive=True),
    backend_url: str = typer.Option(
        "",
        "--backend-url",
        "-b",
        help="Backend URL for self-hosted or custom pureml backend instance",
    ),
):
    """
    Delete secrets using key

    Usage:
    purecli secrets delete "secret_name"
    """
    logger.info(f"Delete secrets for {secret_name}")
    backend_base_url = get_backend_base_url(backend_url)

    # Ask for confirmation
    print()
    confirm = typer.confirm(
        f"Are you sure you want to delete the {secret_name} secrets?"
    )
    if not confirm:
        logger.info("User aborted the operation")
        return

    # Delete secret
    get_org_id()
    url_path = f"secrets/{secret_name}"
    url = urljoin(backend_base_url, url_path)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_JSON)

    response = requests.delete(url, headers=headers)

    if response.ok:
        print(f"[green]Successfully deleted {secret_name} secrets[/green]")
    else:
        logger.error("Unable to delete secrets!", response=response)
        print("[red]Unable to delete secrets!")


if __name__ == "__main__":
    app()
