import json
import platform
import socket
from time import sleep, time
from urllib.parse import urljoin

import ipapi
import requests
import typer
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn

from pureml.cli.helpers import get_auth_headers, save_auth
from pureml.components import delete_token, get_api_token, get_org_id, get_token
from pureml.schema.backend import get_backend_base_url, get_frontend_base_url
from pureml.schema.request import ContentTypeHeader
from pureml.utils.logger import get_logger

from .orgs import select

app = typer.Typer()
logger = get_logger(name="sdk.cli.auth")


def get_location():
    try:
        response = ipapi.location(output="json")
    except BaseException:
        try:
            # print("Getting device details...")
            response = requests.get(
                "https://api64.ipify.org?format=json"
            ).json()
            response = requests.get(
                f"https://ipapi.co/{response['ip']}/json/",
                headers={"User-Agent": "pureml-cli"},
            ).json()
        except BaseException:
            response = {
                "ip": socket.gethostbyname(socket.gethostname()),
                "city": "Unknown",
                "region": "Unknown",
                "country": "Unknown",
            }
    location_data = {
        "ip": response["ip"] or socket.gethostbyname(socket.gethostname()),
        "city": response["city"] or "Unknown",
        "region": response["region"] or "Unknown",
        "country": response["country_name"] or "Unknown",
    }
    return location_data


@app.command()
def details():
    """
    Display details of the current authentication status, including organization ID, access token, and API key.
    """
    token = get_token()
    api_token = get_api_token()
    org_id = get_org_id()

    print("Org Id: ", org_id)
    if token is not None:
        # print("Access Token: ", token)
        print("Logged in using access token")
    if api_token is not None:
        # print("API Key: ", api_token["api_token"])
        print("Logged in using API token")


@app.callback()
def callback():
    """
    Authentication user command

    Use with status, login or logout option

    status - Checks current authenticated user
    login - Logs in user
    logout - Logs out user
    """


@app.command()
def login(
    backend_url: str = typer.Option(
        "",
        "--backend-url",
        "-b",
        help="Backend URL for self-hosted or custom pureml backend instance",
    ),
    frontend_url: str = typer.Option(
        "",
        "--frontend-url",
        "-f",
        help="Frontend URL for self-hosted or custom pureml frontend instance",
    ),
    browserless: bool = typer.Option(
        False,
        "--browserless",
        "-s",
        help="Browserless login for ssh or pipelines",
    ),
    api_token: bool = typer.Option(
        False, "--api-token", "-t", help="Login with api token"
    ),
):
    logger.info("Logging in user")
    try:
        backend_base_url = get_backend_base_url(backend_url)
        frontend_base_url = get_frontend_base_url(frontend_url)
        # API key login
        if api_token:
            logger.info("API token login")
            print("\nEnter your credentials to login/\n")
            api_token: str = typer.prompt("Enter your api token secret")
            save_auth(api_token=api_token)
            select()

        # Browser based login
        else:
            logger.info("Browser based login")
            # Get device details
            device = platform.platform()
            device_data = get_location()
            device_id = device_data["ip"]
            device_location = (
                device_data["city"]
                + ", "
                + device_data["region"]
                + ", "
                + device_data["country"]
            )

            # Create session
            device_data = {
                "device": device,
                "device_id": device_id,
                "device_location": device_location,
            }
            logger.debug("Device data", data=device_data)
            url_path = "users/create-session"
            url = urljoin(backend_base_url, url_path)

            # print(device_data)
            logger.info("Sending request to backend", url=url)
            response = requests.post(url, json=device_data)
            logger.info(
                "Response from backend", response_status=response.status_code
            )

            if not response.ok:
                logger.error("Unable to create session", response=response)
                print(
                    "[red]Unable to create session! Please try again later[/red]"
                )
                return

            session_uuid = response.json()["data"][0]["session_uuid"]

            # Generater link & Open browser
            link = urljoin(
                frontend_base_url, f"auth/verify-session/{session_uuid}"
            )
            print(link)

            if browserless:
                logger.warning("Browserless session verification")
                print(
                    f"Please open the following link in your browser to login: [underline]{link}[/underline]"
                )
            else:
                # Open browser
                logger.info("Opening browser for session verification")
                print(f"Opening the browser : [underline]{link}[/underline]")
                typer.launch(link)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(
                    description="Waiting for response...", total=None
                )
                # Hit the endpoint to check if the session is verified
                start_time = time()
                while True:
                    url_path = "users/session-token"
                    url = urljoin(backend_base_url, url_path)
                    data = {
                        "session_uuid": session_uuid,
                        "device_id": device_id,
                    }
                    # print(data)
                    response = requests.post(url, json=data)
                    # print("Hit API response ", response.text)
                    if response.ok:
                        token = response.text
                        token = json.loads(token)["data"][0]

                        access_token = token["accessToken"]
                        email = token["email"]

                        save_auth(access_token=access_token, email=email)

                        break
                    else:
                        if response.status_code == 404:
                            print(
                                "[red]Session not found! Please try again later[/red]"
                            )
                            return
                        elif response.status_code == 403:
                            print(
                                "[red]Session expired or invalid device! Please try again later[/red]"
                            )
                            return

                    if time() - start_time > 60 * 10:
                        print("[red]Session timed out!")
                        return

                    sleep(1)
            print(f"[green]Successfully logged in as {email}![/green]")

            # Select organization
            select()
            print(
                "Please run `pureml init` in project directory to initialize your project"
            )
    except Exception as e:
        logger.error("Exception occurred while logging in", error=e)
        print(
            f"[red]Unable to contact the server! Please try again later[/red]"
        )


@app.command()
def status():
    logger.info("Checking user status")
    exists = get_auth_headers(
        content_type=ContentTypeHeader.APP_FORM_URL_ENCODED
    )
    logger.info("User status", extra={"exists": exists})  # Correct usage
    if exists:
        print(f"[green]You are logged in![/green]")


@app.command()
def logout():
    exists = get_auth_headers(
        content_type=ContentTypeHeader.APP_FORM_URL_ENCODED
    )
    if exists:
        logger.info("Logging out user")
        delete_token()


if __name__ == "__main__":
    app()
