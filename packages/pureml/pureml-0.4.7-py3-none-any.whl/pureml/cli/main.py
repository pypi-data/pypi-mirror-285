from pathlib import Path

import typer
from dotenv import load_dotenv
from rich import print
from rich.table import Table

import pureml.cli.auth as auth
import pureml.cli.orgs as orgs
import pureml.cli.secrets as secrets
from pureml.cli.helpers import get_auth_headers
from pureml.cli.puremlconfig import PureMLConfigYML
from pureml.utils.logger import get_logger

# from puretrainer.train import Trainer

load_dotenv()


logger = get_logger(name="sdk.cli.main")
app = typer.Typer(no_args_is_help=True)
app.add_typer(auth.app, name="auth")
app.add_typer(secrets.app, name="secrets")
app.add_typer(orgs.app, name="orgs")


def print_version(value: bool):
    if value:
        from pureml import __version__

        print(f"PureML SDK version: {__version__}")
        raise typer.Exit()


@app.callback()
def callback(
    version: bool = typer.Option(
        None, "--version", "-v", callback=print_version, is_eager=True
    ),
):
    """
    PureML CLI

    This is the official CLI for PureML.
    """


# init the config file
@app.command()
def init(
    silent: bool = typer.Option(
        False, "--silent", "-s", help="Run in silent mode"
    ),
    repository: str = typer.Option(
        None, "--repository", "-r", help="The repository to use"
    ),
    backend_url: str = typer.Option(
        None, "--backend-url", "-b", help="The backend url to use"
    ),
    frontend_url: str = typer.Option(
        None, "--frontend-url", "-f", help="The frontend url to use"
    ),
):
    """
    This command will initialize the puremlconfig.yaml file for your project
    """
    project_path = Path.cwd()
    puremlconfig = PureMLConfigYML(project_path / "puremlconfig.yaml")
    headers = get_auth_headers()
    if headers is None:
        return

    # check if the config file exists
    if puremlconfig.file.exists():
        logger.warning(
            "A puremlconfig.yaml file already exists in this directory - aborting"
        )
        print(
            "A puremlconfig.yaml file already exists in this directory - aborting"
        )
        return

    # if not silent, ask for the config values
    if not silent:
        print("Let's get started with the configuration of your project")

        repository_path = ""
        if not repository:
            table = Table("Sr.No.", "Storage Repository")
            table.add_row("1 (default)", "Local file system")
            table.add_row("2", "AWS S3")
            table.add_row("3", "Cloudflare R2")
            print(table)
            repository = None
            while repository not in [1, 2, 3]:
                repository = typer.prompt(
                    "Enter the Sr.No. of your preferred storage repository (1, 2 or 3)",
                    default=1,
                    show_default=False,
                )

            logger.info(f"Selected repository: {repository}")
            if repository == 1:
                path = typer.prompt(
                    "Enter the path to your local repository [default: pureml_data/]",
                    default="pureml_data/",
                    show_default=False,
                )
                repository_path = "file://" + path
            elif repository == 2 or repository == 3:
                print(
                    "If not already done, please integrate your storage repository by adding secrets using `pureml secrets add`"
                )
                added_secret = typer.confirm(
                    "Have you added your storage repository secrets? (y/n)",
                    default=True,
                )
                if not added_secret:
                    print(
                        "Please add your storage repository secrets using `pureml secrets add` or using UI"
                    )
                    return
                secret_name = typer.prompt(
                    "Enter the name of your integrated secret"
                )
                if repository_path == 2:
                    repository_path = f"s3://{secret_name}"
                else:
                    repository_path = f"r2://{secret_name}"

        else:
            print(f"Using given repository: {repository}")

        isSelfHosted = typer.confirm(
            "Are you using a self-hosted PureML instance?"
        )
        logger.info(f"Is self-hosted: {isSelfHosted}")
        if isSelfHosted:
            if not backend_url:
                backend_url = typer.prompt(
                    "Enter the backend url",
                    default="http://localhost:8080/api/v1/",
                )
            else:
                print(f"Using given backend url: {backend_url}")

            if not frontend_url:
                frontend_url = typer.prompt(
                    "Enter the frontend url", default="http://localhost:3000/"
                )
            else:
                print(f"Using given frontend url: {frontend_url}")
    else:
        if not repository:
            print("Missing required arguments")
            return
        print(f"Using repository: {repository_path}")
        if backend_url:
            print(f"Using given backend url: {backend_url}")
        if frontend_url:
            print(f"Using given frontend url: {frontend_url}")

    # create the config file
    data = {
        "repository": repository_path,
    }
    if backend_url:
        data["backend_url"] = backend_url
    if frontend_url:
        data["frontend_url"] = frontend_url
    puremlconfig.save(data)
    print(
        "[green]Created configuration file puremlconfig.yaml in current directory[/green]"
    )
